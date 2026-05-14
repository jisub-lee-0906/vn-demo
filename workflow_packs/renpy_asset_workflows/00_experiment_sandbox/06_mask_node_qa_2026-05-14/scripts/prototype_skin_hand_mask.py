#!/usr/bin/env python3
"""Prototype skin-only hand mask candidates without external Python deps.

Reads ComfyUI node-QA source/mask PNGs and writes candidate masks/contact sheets.
This is intentionally separate from canonical ComfyUI nodes until masks pass.
"""
from __future__ import annotations
import argparse, pathlib, struct, zlib, itertools, collections, math

PNG_SIG = b'\x89PNG\r\n\x1a\n'

def read_png(path):
    data = pathlib.Path(path).read_bytes()
    assert data.startswith(PNG_SIG), path
    pos = 8; w = h = ct = bd = None; raw = b''
    while pos < len(data):
        ln = struct.unpack('>I', data[pos:pos+4])[0]; pos += 4
        typ = data[pos:pos+4]; pos += 4
        chunk = data[pos:pos+ln]; pos += ln
        pos += 4
        if typ == b'IHDR':
            w,h,bd,ct,comp,flt,inter = struct.unpack('>IIBBBBB', chunk)
            assert bd == 8 and comp == 0 and flt == 0 and inter == 0, (bd,comp,flt,inter)
        elif typ == b'IDAT': raw += chunk
        elif typ == b'IEND': break
    chans = {0:1,2:3,4:2,6:4}[ct]
    bpp = chans
    dec = zlib.decompress(raw)
    stride = w * chans
    rows=[]; i=0; prev=[0]*stride
    for y in range(h):
        f = dec[i]; i += 1
        cur = list(dec[i:i+stride]); i += stride
        out = [0]*stride
        for x in range(stride):
            a = out[x-bpp] if x >= bpp else 0
            b = prev[x]
            c = prev[x-bpp] if x >= bpp else 0
            if f == 0: val = cur[x]
            elif f == 1: val = (cur[x] + a) & 255
            elif f == 2: val = (cur[x] + b) & 255
            elif f == 3: val = (cur[x] + ((a+b)//2)) & 255
            elif f == 4:
                p = a+b-c; pa=abs(p-a); pb=abs(p-b); pc=abs(p-c)
                pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                val = (cur[x] + pr) & 255
            else: raise ValueError(f)
            out[x]=val
        rows.append(out); prev=out
    return w,h,chans,rows

def write_png_gray(path,w,h,vals):
    raw=bytearray()
    for y in range(h):
        raw.append(0)
        raw.extend(vals[y*w:(y+1)*w])
    comp=zlib.compress(bytes(raw),9)
    def chunk(t,d): return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    out=PNG_SIG+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,0,0,0,0))+chunk(b'IDAT',comp)+chunk(b'IEND',b'')
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(path).write_bytes(out)

def write_png_rgb(path,w,h,vals):
    raw=bytearray()
    for y in range(h):
        raw.append(0); raw.extend(vals[y*w*3:(y+1)*w*3])
    comp=zlib.compress(bytes(raw),6)
    def chunk(t,d): return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    out=PNG_SIG+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',comp)+chunk(b'IEND',b'')
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(path).write_bytes(out)

def rgb_arrays(path):
    w,h,c,rows=read_png(path); pix=[]
    for row in rows:
        if c == 4:
            for i in range(0,len(row),4): pix.append((row[i],row[i+1],row[i+2]))
        elif c == 3:
            for i in range(0,len(row),3): pix.append((row[i],row[i+1],row[i+2]))
        elif c == 1:
            for v in row: pix.append((v,v,v))
        else: raise NotImplementedError(c)
    return w,h,pix

def gray_mask(path, thr=16):
    w,h,c,rows=read_png(path); out=bytearray(w*h); k=0
    for row in rows:
        if c in (3,4):
            step=c
            for i in range(0,len(row),step):
                out[k]=255 if max(row[i],row[i+1],row[i+2])>thr else 0; k+=1
        elif c == 1:
            for v in row: out[k]=255 if v>thr else 0; k+=1
        else: raise NotImplementedError(c)
    return w,h,out

def bbox(mask,w,h):
    xs=[]; ys=[]
    for y in range(h):
        off=y*w
        for x in range(w):
            if mask[off+x]: xs.append(x); ys.append(y)
    if not xs: return None
    return min(xs),min(ys),max(xs),max(ys)

def dilate(mask,w,h,r):
    if r<=0: return bytearray(mask)
    out=bytearray(w*h)
    pts=[(dx,dy) for dy in range(-r,r+1) for dx in range(-r,r+1) if dx*dx+dy*dy<=r*r]
    for y in range(h):
        off=y*w
        for x in range(w):
            if mask[off+x]:
                for dx,dy in pts:
                    xx=x+dx; yy=y+dy
                    if 0<=xx<w and 0<=yy<h: out[yy*w+xx]=255
    return out

def erode(mask,w,h,r):
    if r<=0: return bytearray(mask)
    out=bytearray(w*h); pts=[(dx,dy) for dy in range(-r,r+1) for dx in range(-r,r+1) if dx*dx+dy*dy<=r*r]
    for y in range(h):
        for x in range(w):
            ok=True
            for dx,dy in pts:
                xx=x+dx; yy=y+dy
                if not (0<=xx<w and 0<=yy<h and mask[yy*w+xx]): ok=False; break
            if ok: out[y*w+x]=255
    return out

def close(mask,w,h,r): return erode(dilate(mask,w,h,r),w,h,r)

def components(mask,w,h):
    seen=bytearray(w*h); comps=[]
    for idx,v in enumerate(mask):
        if not v or seen[idx]: continue
        q=[idx]; seen[idx]=1; pts=[]
        while q:
            p=q.pop(); pts.append(p); x=p%w; y=p//w
            for nx,ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                if 0<=nx<w and 0<=ny<h:
                    ni=ny*w+nx
                    if mask[ni] and not seen[ni]: seen[ni]=1; q.append(ni)
        comps.append(pts)
    return comps

def make_candidate(src_path,char_path,existing_path,outdir,slug):
    w,h,pix=rgb_arrays(src_path)
    w2,h2,char=gray_mask(char_path); w3,h3,existing=gray_mask(existing_path)
    assert (w,h)==(w2,h2)==(w3,h3)
    bb=bbox(char,w,h); assert bb
    x1,y1,x2,y2=bb; cw=x2-x1+1; ch=y2-y1+1
    roi=bytearray(w*h); side_w=int(cw*0.42); ys=int(y1+ch*0.58); ye=int(y1+ch*0.985)
    hand_floor=int(y1+ch*0.74)
    for y in range(max(0,ys),min(h,ye+1)):
        for x in itertools.chain(range(max(0,x1),min(w,x1+side_w)), range(max(0,x2-side_w+1),min(w,x2+1))):
            if char[y*w+x]: roi[y*w+x]=255
    # skin: deliberately strict red/orange skin, excluding beige cardigan/cuff as much as possible
    skin=bytearray(w*h); score=bytearray(w*h)
    for i,(r,g,b) in enumerate(pix):
        mx=max(r,g,b); mn=min(r,g,b); sat=mx-mn; lum=(r*54+g*183+b*19)//256
        red_skin = (r>135 and g>70 and b>45 and lum>95 and lum<235 and sat>28 and (r-g)>24 and (r-b)>42 and (g-b)>-6)
        # recover pale fingertips: close to existing Florence hand, still warmer/redder than cardigan
        pale_skin = (r>175 and g>125 and b>105 and lum<245 and sat>18 and (r-g)>18 and (r-b)>34 and existing[i] and roi[i])
        if (red_skin or pale_skin) and roi[i] and (i//w) >= hand_floor:
            skin[i]=255
            score[i]=min(255, max(0, (r-g)*3 + (r-b)))
    near_existing=dilate(existing,w,h,18)
    lower_side_prior=bytearray(w*h)
    for i in range(w*h):
        y=i//w; x=i%w
        outer = x < x1 + cw*0.18 or x > x2 - cw*0.18
        if roi[i] and y >= hand_floor and outer:
            lower_side_prior[i]=255
    seed=bytearray(w*h)
    for i in range(w*h):
        if skin[i] and (existing[i] or near_existing[i] or lower_side_prior[i]): seed[i]=255
    seed=close(seed,w,h,2)
    # keep plausible hand components: lower side, small-ish, not tall sleeve columns
    final=bytearray(w*h)
    kept=bytearray(w*h)
    for pts in components(seed,w,h):
        area=len(pts); xs=[p%w for p in pts]; ys2=[p//w for p in pts]
        bx1,by1,bx2,by2=min(xs),min(ys2),max(xs),max(ys2); bw=bx2-bx1+1; bh=by2-by1+1
        cy=sum(ys2)/area; cx=sum(xs)/area
        side = cx < (x1+x2)/2 or cx > (x1+x2)/2
        plausible = 20 <= area <= 26000 and 3 <= bw <= cw*0.34 and 4 <= bh <= ch*0.46 and cy > y1+ch*0.60
        if plausible:
            # Components may include warm cardigan cuff/sleeve connected to the hand.
            # Keep only the lower terminal portion where the actual relaxed hand is.
            trim_top = max(by1, by2 - int(min(95, max(38, bh * 0.38))))
            for p in pts:
                y=p//w; x=p%w
                outer = x < x1 + cw*0.22 or x > x2 - cw*0.22
                if y >= trim_top and y >= hand_floor and outer:
                    kept[p]=255
    # final soft-ish but not blocky: grow only 1 px after strict skin
    final=dilate(kept,w,h,1)
    for i in range(w*h): final[i]=255 if final[i] and roi[i] else 0
    # overlay debug RGB
    overlay=bytearray(w*h*3)
    for i,(r,g,b) in enumerate(pix):
        rr,gg,bbv=r,g,b
        if roi[i]: rr=(rr*2+255)//3; gg=(gg*2+220)//3
        if skin[i]: gg=255; rr//=2; bbv//=2
        if existing[i]: bbv=255
        if final[i]: rr=255; gg=40; bbv=40
        overlay[i*3:i*3+3]=bytes((rr,gg,bbv))
    out=pathlib.Path(outdir); out.mkdir(parents=True,exist_ok=True)
    write_png_gray(out/f'{slug}_a_roi.png',w,h,roi)
    write_png_gray(out/f'{slug}_b_skin_strict.png',w,h,skin)
    write_png_gray(out/f'{slug}_c_seed_near_florence.png',w,h,seed)
    write_png_gray(out/f'{slug}_d_component_kept.png',w,h,kept)
    write_png_gray(out/f'{slug}_e_final_hand_skinmask.png',w,h,final)
    write_png_rgb(out/f'{slug}_f_overlay.png',w,h,overlay)
    return out/f'{slug}_e_final_hand_skinmask.png'

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--run-dir',required=True); ap.add_argument('--out-dir',required=True); ap.add_argument('--slug',action='append',required=True)
    args=ap.parse_args(); rd=pathlib.Path(args.run_dir)
    for slug in args.slug:
        def one(prefix):
            m=sorted(rd.glob(f'{prefix}_{slug}_*.png'))
            if not m: raise FileNotFoundError((prefix,slug,rd))
            return m[-1]
        make_candidate(one('00_source'), one('01_char_alpha'), one('06_union_plus_fingers'), args.out_dir, slug)
        print(slug, 'done')
if __name__=='__main__': main()
