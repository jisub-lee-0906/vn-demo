import torch
import torch.nn.functional as F


class VN_AutoCollarCleanupMask:
    """Deterministic neck/collar remnant mask for VN outfit cleanup.

    Inputs are ComfyUI IMAGE (B,H,W,C float 0..1) and MASK (B,H,W float 0..1).
    The node constrains detection to a dynamic neck/chest ROI derived from the
    protected head/hair/face mask and the character silhouette, then searches
    for old collar/bow remnants. It intentionally fails closed when the mask is
    too large or outside the ROI so hoodie pockets/hem are not edited.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "character_mask": ("MASK",),
                "protect_mask": ("MASK",),
                "mode": (["hoodie_collar_bow", "white_collar_only", "blue_bow_only"], {"default": "hoodie_collar_bow"}),
                "roi_top_pad": ("INT", {"default": 24, "min": -256, "max": 512, "step": 1}),
                "roi_height": ("INT", {"default": 390, "min": 64, "max": 1024, "step": 1}),
                "roi_width_scale": ("FLOAT", {"default": 0.55, "min": 0.10, "max": 1.00, "step": 0.01}),
                "candidate_threshold": ("FLOAT", {"default": 0.50, "min": 0.05, "max": 1.00, "step": 0.01}),
                "max_coverage": ("FLOAT", {"default": 0.055, "min": 0.001, "max": 0.500, "step": 0.001}),
                "min_coverage": ("FLOAT", {"default": 0.0002, "min": 0.0, "max": 0.050, "step": 0.0001}),
                "grow": ("INT", {"default": 18, "min": 0, "max": 128, "step": 1}),
                "blur": ("INT", {"default": 7, "min": 0, "max": 127, "step": 2}),
            }
        }

    RETURN_TYPES = ("MASK", "MASK", "MASK", "IMAGE", "FLOAT")
    RETURN_NAMES = ("cleanup_mask", "roi_mask", "candidate_mask", "debug_overlay", "coverage")
    FUNCTION = "make_mask"
    CATEGORY = "VN/masks"

    def make_mask(
        self,
        image,
        character_mask,
        protect_mask,
        mode,
        roi_top_pad,
        roi_height,
        roi_width_scale,
        candidate_threshold,
        max_coverage,
        min_coverage,
        grow,
        blur,
    ):
        device = image.device
        img = image.float().clamp(0, 1)
        b, h, w, c = img.shape
        char = self._fit_mask(character_mask, b, h, w, device) > 0.20
        prot = self._fit_mask(protect_mask, b, h, w, device) > 0.20

        cleanup_list = []
        roi_list = []
        cand_list = []
        debug_list = []
        cov_values = []

        for i in range(b):
            im = img[i]
            cm = char[i]
            pm = prot[i]
            roi = self._neck_roi(cm, pm, h, w, roi_top_pad, roi_height, roi_width_scale)
            allowed = roi & cm & (~self._dilate_bool(pm, 10))
            candidate = self._remnant_candidates(im, allowed, mode, candidate_threshold)

            # Smooth/grow only after fail-closed area checks on the raw candidate.
            raw_area = float(candidate.float().mean().item())
            roi_area = max(float(roi.float().mean().item()), 1e-8)
            rel_to_roi = raw_area / roi_area

            if raw_area < min_coverage or raw_area > max_coverage or rel_to_roi > 0.55:
                clean = torch.zeros((h, w), dtype=torch.float32, device=device)
            else:
                clean_bool = candidate
                if grow > 0:
                    clean_bool = self._dilate_bool(clean_bool, grow)
                clean_bool = clean_bool & allowed
                clean = clean_bool.float()
                if blur and blur > 1:
                    clean = self._blur_mask(clean, blur)
                    clean = (clean * allowed.float()).clamp(0, 1)

            cleanup_list.append(clean)
            roi_list.append(roi.float())
            cand_list.append(candidate.float())
            cov_values.append(float(clean.mean().item()))
            debug_list.append(self._debug_overlay(im, roi.float(), candidate.float(), clean))

        cleanup = torch.stack(cleanup_list, dim=0)
        roi_mask = torch.stack(roi_list, dim=0)
        candidate_mask = torch.stack(cand_list, dim=0)
        debug = torch.stack(debug_list, dim=0)
        coverage = float(sum(cov_values) / max(len(cov_values), 1))
        return cleanup, roi_mask, candidate_mask, debug, coverage

    def _fit_mask(self, mask, b, h, w, device):
        m = mask.float().to(device)
        if m.dim() == 2:
            m = m.unsqueeze(0)
        if m.dim() == 4:
            # Accept accidental image-like masks by taking the first channel.
            m = m[..., 0]
        if m.shape[0] == 1 and b > 1:
            m = m.repeat(b, 1, 1)
        if m.shape[-2:] != (h, w):
            m = F.interpolate(m.unsqueeze(1), size=(h, w), mode="bilinear", align_corners=False).squeeze(1)
        return m.clamp(0, 1)

    def _bbox(self, mask_bool, h, w):
        ys, xs = torch.where(mask_bool)
        if ys.numel() == 0:
            return None
        return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())

    def _neck_roi(self, char, prot, h, w, top_pad, roi_height, width_scale):
        cb = self._bbox(char, h, w)
        if cb is None:
            return torch.zeros((h, w), dtype=torch.bool, device=char.device)
        px1, py1, px2, py2 = self._bbox(prot, h, w) or cb
        cx1, cy1, cx2, cy2 = cb
        char_w = max(cx2 - cx1 + 1, 1)
        center_x = (cx1 + cx2) // 2
        roi_w = int(char_w * width_scale)
        x1 = max(0, center_x - roi_w // 2)
        x2 = min(w - 1, center_x + roi_w // 2)
        # Start slightly above the protected head/hair bottom so collar under bangs is included.
        y1 = max(0, py2 - int(top_pad))
        y2 = min(h - 1, y1 + int(roi_height))
        roi = torch.zeros((h, w), dtype=torch.bool, device=char.device)
        roi[y1 : y2 + 1, x1 : x2 + 1] = True
        return roi

    def _remnant_candidates(self, im, allowed, mode, threshold):
        r = im[..., 0]
        g = im[..., 1]
        b = im[..., 2]
        maxc = torch.maximum(torch.maximum(r, g), b)
        minc = torch.minimum(torch.minimum(r, g), b)
        sat = maxc - minc
        lum = 0.2126 * r + 0.7152 * g + 0.0722 * b

        # Old white shirt/collar fragments: bright, low saturation, not lavender/pink.
        white = (lum > 0.68) & (sat < 0.23) & allowed

        # Old blue bow/ribbon fragments. Require blue dominance so lavender hoodie shadows are ignored.
        blue = (b > 0.24) & (b > r + 0.07) & (b > g + 0.04) & (sat > 0.10) & allowed

        # Very dark collar/bow line fragments near the neck. Conservative to avoid hoodie folds.
        dark = (lum < 0.18) & (sat > 0.04) & allowed

        if mode == "white_collar_only":
            cand = white
        elif mode == "blue_bow_only":
            cand = blue | dark
        else:
            cand = white | blue | dark

        # Remove very weak/noisy candidates by a local density test.
        if threshold > 0:
            density = F.avg_pool2d(cand.float().unsqueeze(0).unsqueeze(0), kernel_size=9, stride=1, padding=4).squeeze()
            cand = cand & (density > (threshold * 0.08))
        return cand

    def _dilate_bool(self, mask_bool, radius):
        if radius <= 0:
            return mask_bool
        k = radius * 2 + 1
        x = mask_bool.float().unsqueeze(0).unsqueeze(0)
        y = F.max_pool2d(x, kernel_size=k, stride=1, padding=radius).squeeze()
        return y > 0.0

    def _erode_bool(self, mask_bool, radius):
        if radius <= 0:
            return mask_bool
        inv = ~mask_bool
        return ~self._dilate_bool(inv, radius)

    def _blur_mask(self, mask, kernel):
        # Simple box blur; sufficient for inpaint feathering and dependency-free.
        if kernel <= 1:
            return mask
        if kernel % 2 == 0:
            kernel += 1
        pad = kernel // 2
        x = mask.float().unsqueeze(0).unsqueeze(0)
        y = F.avg_pool2d(x, kernel_size=kernel, stride=1, padding=pad).squeeze()
        return y.clamp(0, 1)

    def _debug_overlay(self, im, roi, candidate, cleanup):
        out = im.clone()
        # ROI: faint yellow, raw candidate: red, final cleanup: green.
        out = torch.where(roi.unsqueeze(-1) > 0.5, out * 0.72 + torch.tensor([0.28, 0.24, 0.0], device=im.device), out)
        out = torch.where(candidate.unsqueeze(-1) > 0.5, out * 0.35 + torch.tensor([0.65, 0.0, 0.0], device=im.device), out)
        out = torch.where(cleanup.unsqueeze(-1) > 0.05, out * 0.35 + torch.tensor([0.0, 0.65, 0.0], device=im.device), out)
        return out.clamp(0, 1)


class VN_AlphaEdgeRefine(VN_AutoCollarCleanupMask):
    """Conservative RGBA alpha-edge cleanup for VN transparent sprites.

    This node is intended to run after BiRefNetRMBG(background=Alpha). It does
    not re-segment the character. Instead, it refines the produced alpha matte:
    - removes tiny detached alpha islands/speckles outside the main silhouette;
    - cuts very faint exterior alpha pixels that often become visible residue on
      dark/light Ren'Py composites;
    - keeps connected hair/clothing/hand edges by default.

    Inputs and outputs use ComfyUI IMAGE tensors. If the incoming IMAGE has no
    alpha channel, the image is passed through and the removed mask is empty.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "alpha_threshold": ("FLOAT", {"default": 0.015, "min": 0.0, "max": 0.50, "step": 0.001}),
                "edge_alpha_cut": ("FLOAT", {"default": 0.045, "min": 0.0, "max": 0.50, "step": 0.001}),
                "island_min_area": ("INT", {"default": 96, "min": 0, "max": 10000, "step": 1}),
                "bridge_radius": ("INT", {"default": 1, "min": 0, "max": 16, "step": 1}),
                "edge_width": ("INT", {"default": 2, "min": 0, "max": 16, "step": 1}),
                "max_removed_coverage": ("FLOAT", {"default": 0.030, "min": 0.001, "max": 0.500, "step": 0.001}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "MASK", "IMAGE", "FLOAT")
    RETURN_NAMES = ("refined_image", "refined_alpha", "removed_mask", "debug_overlay", "removed_coverage")
    FUNCTION = "refine_alpha"
    CATEGORY = "VN/masks"

    def refine_alpha(self, image, alpha_threshold, edge_alpha_cut, island_min_area, bridge_radius, edge_width, max_removed_coverage):
        device = image.device
        img = image.float().clamp(0, 1)
        b, h, w, c = img.shape
        if c < 4:
            empty = torch.zeros((b, h, w), dtype=torch.float32, device=device)
            return img, empty, empty, img, 0.0

        rgb = img[..., :3]
        alpha = img[..., 3].clamp(0, 1)
        refined_list, removed_list, debug_list, cov_values = [], [], [], []

        for i in range(b):
            a = alpha[i]
            fg = a > float(alpha_threshold)
            if bridge_radius > 0:
                fg = self._erode_bool(self._dilate_bool(fg, int(bridge_radius)), int(bridge_radius))

            keep = self._keep_connected_components(fg, int(island_min_area))

            # Connected exterior wisps/rims can survive component filtering. Only
            # trim the faint alpha band near the silhouette boundary; opaque line
            # art and hair pixels stay intact.
            if edge_width > 0 and edge_alpha_cut > 0:
                core = self._erode_bool(keep, int(edge_width))
                edge_band = keep & (~core)
                faint_edge = edge_band & (a < float(edge_alpha_cut))
                keep = keep & (~faint_edge)

            cleaned_alpha = torch.where(keep, a, torch.zeros_like(a))
            removed = (a > float(alpha_threshold)) & (cleaned_alpha <= float(alpha_threshold))
            removed_cov = float(removed.float().mean().item())

            # Fail closed: if settings would remove too much, pass through. This
            # prevents accidental hair/hand/clothing erosion on unusual sprites.
            if removed_cov > float(max_removed_coverage):
                cleaned_alpha = a
                removed = torch.zeros_like(removed)
                removed_cov = 0.0

            refined_list.append(cleaned_alpha)
            removed_list.append(removed.float())
            cov_values.append(removed_cov)
            debug_list.append(self._alpha_debug_overlay(rgb[i], a, cleaned_alpha, removed.float()))

        refined_alpha = torch.stack(refined_list, dim=0).clamp(0, 1)
        removed_mask = torch.stack(removed_list, dim=0).clamp(0, 1)
        refined = torch.cat([rgb, refined_alpha.unsqueeze(-1)], dim=-1).clamp(0, 1)
        debug = torch.stack(debug_list, dim=0).clamp(0, 1)
        coverage = float(sum(cov_values) / max(len(cov_values), 1))
        return refined, refined_alpha, removed_mask, debug, coverage

    def _erode_bool(self, mask_bool, radius):
        if radius <= 0:
            return mask_bool
        inv = ~mask_bool
        return ~self._dilate_bool(inv, radius)

    def _keep_connected_components(self, mask_bool, min_area):
        # CPU flood fill is dependency-free and fast enough for single VN sprites.
        h, w = mask_bool.shape
        m = mask_bool.detach().to("cpu").bool()
        visited = torch.zeros((h, w), dtype=torch.bool)
        keep_cpu = torch.zeros((h, w), dtype=torch.bool)
        components = []

        ys, xs = torch.where(m)
        if ys.numel() == 0:
            return keep_cpu.to(mask_bool.device)

        for y0, x0 in zip(ys.tolist(), xs.tolist()):
            if visited[y0, x0]:
                continue
            stack = [(y0, x0)]
            visited[y0, x0] = True
            coords = []
            while stack:
                y, x = stack.pop()
                coords.append((y, x))
                for ny in (y - 1, y, y + 1):
                    for nx in (x - 1, x, x + 1):
                        if ny == y and nx == x:
                            continue
                        if 0 <= ny < h and 0 <= nx < w and (not visited[ny, nx]) and m[ny, nx]:
                            visited[ny, nx] = True
                            stack.append((ny, nx))
            components.append(coords)

        if not components:
            return keep_cpu.to(mask_bool.device)

        largest_idx = max(range(len(components)), key=lambda idx: len(components[idx]))
        for idx, coords in enumerate(components):
            if idx == largest_idx or len(coords) >= max(int(min_area), 0):
                for y, x in coords:
                    keep_cpu[y, x] = True
        return keep_cpu.to(mask_bool.device)

    def _alpha_debug_overlay(self, rgb, old_alpha, new_alpha, removed):
        # Red = removed residue; green = kept alpha silhouette.
        out = rgb.clone()
        kept_edge = new_alpha > 0.015
        out = torch.where(kept_edge.unsqueeze(-1), out * 0.82 + torch.tensor([0.0, 0.18, 0.0], device=rgb.device), out)
        out = torch.where(removed.unsqueeze(-1) > 0.5, out * 0.25 + torch.tensor([0.75, 0.0, 0.0], device=rgb.device), out)
        return out.clamp(0, 1)


class VN_AutoTrimCleanupMask(VN_AutoCollarCleanupMask):
    """Fail-closed old trim/color cleanup mask for 06 outfit outputs.

    This is intentionally narrower than the full edit mask. It searches only the
    hoodie hem, sleeve cuff, and lower-skirt bands for old cream/yellow/beige or
    unwanted dark-skirt remnants after the main outfit pass. Hands/head/hair are
    excluded by the supplied protection mask, and candidates must stay under a
    small coverage cap before grow/blur.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "character_mask": ("MASK",),
                "edit_mask": ("MASK",),
                "protect_mask": ("MASK",),
                "mode": (["cream_trim_and_lower_dark", "cream_trim_only", "lower_dark_only"], {"default": "cream_trim_and_lower_dark"}),
                "hem_y_ratio": ("FLOAT", {"default": 0.70, "min": 0.35, "max": 0.95, "step": 0.01}),
                "hem_height_ratio": ("FLOAT", {"default": 0.10, "min": 0.02, "max": 0.30, "step": 0.01}),
                "cuff_y_ratio": ("FLOAT", {"default": 0.62, "min": 0.35, "max": 0.95, "step": 0.01}),
                "cuff_side_width_ratio": ("FLOAT", {"default": 0.28, "min": 0.08, "max": 0.50, "step": 0.01}),
                "lower_y_ratio": ("FLOAT", {"default": 0.77, "min": 0.45, "max": 0.98, "step": 0.01}),
                "cream_threshold": ("FLOAT", {"default": 0.12, "min": 0.02, "max": 0.45, "step": 0.01}),
                "dark_lum_max": ("FLOAT", {"default": 0.32, "min": 0.05, "max": 0.70, "step": 0.01}),
                "min_coverage": ("FLOAT", {"default": 0.00005, "min": 0.0, "max": 0.050, "step": 0.00005}),
                "max_coverage": ("FLOAT", {"default": 0.050, "min": 0.001, "max": 0.200, "step": 0.001}),
                "grow": ("INT", {"default": 7, "min": 0, "max": 64, "step": 1}),
                "blur": ("INT", {"default": 5, "min": 0, "max": 63, "step": 2}),
            }
        }

    RETURN_TYPES = ("MASK", "MASK", "MASK", "IMAGE", "FLOAT")
    RETURN_NAMES = ("cleanup_mask", "roi_mask", "candidate_mask", "debug_overlay", "coverage")
    FUNCTION = "make_mask"
    CATEGORY = "VN/masks"

    def make_mask(self, image, character_mask, edit_mask, protect_mask, mode, hem_y_ratio, hem_height_ratio, cuff_y_ratio, cuff_side_width_ratio, lower_y_ratio, cream_threshold, dark_lum_max, min_coverage, max_coverage, grow, blur):
        device = image.device
        img = image.float().clamp(0, 1)
        b, h, w, c = img.shape
        char = self._fit_mask(character_mask, b, h, w, device) > 0.12
        edit = self._fit_mask(edit_mask, b, h, w, device) > 0.05
        prot = self._fit_mask(protect_mask, b, h, w, device) > 0.05
        cleanup_list, roi_list, cand_list, debug_list, cov_values = [], [], [], [], []
        for i in range(b):
            im = img[i]
            cm = char[i]
            em = edit[i]
            pm = prot[i]
            cb = self._bbox(cm, h, w)
            roi = torch.zeros((h, w), dtype=torch.bool, device=device)
            lower_roi = torch.zeros((h, w), dtype=torch.bool, device=device)
            if cb is not None:
                x1, y1, x2, y2 = cb
                char_w = max(x2 - x1 + 1, 1)
                char_h = max(y2 - y1 + 1, 1)
                center_x = (x1 + x2) // 2
                hem_y1 = int(y1 + char_h * float(hem_y_ratio))
                hem_y2 = min(y2, hem_y1 + max(8, int(char_h * float(hem_height_ratio))))
                hem_half = int(char_w * 0.28)
                roi[max(y1, hem_y1):hem_y2 + 1, max(x1, center_x - hem_half):min(x2 + 1, center_x + hem_half)] = True

                cuff_y1 = int(y1 + char_h * float(cuff_y_ratio))
                side_w = max(1, int(char_w * float(cuff_side_width_ratio)))
                roi[cuff_y1:y2 + 1, x1:min(x2 + 1, x1 + side_w)] = True
                roi[cuff_y1:y2 + 1, max(x1, x2 - side_w + 1):x2 + 1] = True

                lower_y1 = int(y1 + char_h * float(lower_y_ratio))
                lower_roi[lower_y1:y2 + 1, x1:x2 + 1] = True
                if mode != "cream_trim_only":
                    roi = roi | lower_roi
                roi = roi & self._dilate_bool(cm, 4)

            allowed = roi & cm & em & (~self._dilate_bool(pm, 3))
            r, g, bl = im[..., 0], im[..., 1], im[..., 2]
            maxc = torch.maximum(torch.maximum(r, g), bl)
            minc = torch.minimum(torch.minimum(r, g), bl)
            sat = maxc - minc
            lum = 0.2126 * r + 0.7152 * g + 0.0722 * bl
            cream = (r > 0.50) & (g > 0.42) & ((r - bl) > float(cream_threshold)) & ((g - bl) > float(cream_threshold) * 0.55) & (lum > 0.45) & allowed
            lower_dark = (lum < float(dark_lum_max)) & (sat > 0.04) & lower_roi & allowed
            if mode == "cream_trim_only":
                candidate = cream
            elif mode == "lower_dark_only":
                candidate = lower_dark
            else:
                candidate = cream | lower_dark

            raw_area = float(candidate.float().mean().item())
            roi_area = max(float(roi.float().mean().item()), 1e-8)
            # Hem/cuff ROIs can legitimately be mostly cream/yellow when the old
            # rib trim survived. Keep the global coverage gate fail-closed, but
            # do not reject a local trim ROI just because the ROI is dense.
            if raw_area < min_coverage or raw_area > max_coverage or (raw_area / roi_area) > 0.92:
                clean = torch.zeros((h, w), dtype=torch.float32, device=device)
            else:
                clean_bool = candidate
                if grow > 0:
                    clean_bool = self._dilate_bool(clean_bool, int(grow))
                clean_bool = clean_bool & allowed
                clean = clean_bool.float()
                if blur and blur > 1:
                    clean = self._blur_mask(clean, int(blur))
                    clean = (clean * allowed.float()).clamp(0, 1)
            cleanup_list.append(clean)
            roi_list.append(roi.float())
            cand_list.append(candidate.float())
            cov_values.append(float(clean.mean().item()))
            debug_list.append(self._debug_overlay(im, roi.float(), candidate.float(), clean))
        return (
            torch.stack(cleanup_list, dim=0),
            torch.stack(roi_list, dim=0),
            torch.stack(cand_list, dim=0),
            torch.stack(debug_list, dim=0),
            float(sum(cov_values) / max(len(cov_values), 1)),
        )


class VN_AutoMaskedColorNormalize(VN_AutoCollarCleanupMask):
    """Deterministically normalize small masked old-color remnants.

    Use after fail-closed trim masks when local inpaint keeps source cream/yellow
    tint. It preserves line/detail luminance while shifting masked pixels toward a
    target garment color.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
                "target_r": ("FLOAT", {"default": 0.86, "min": 0.0, "max": 1.0, "step": 0.01}),
                "target_g": ("FLOAT", {"default": 0.76, "min": 0.0, "max": 1.0, "step": 0.01}),
                "target_b": ("FLOAT", {"default": 0.94, "min": 0.0, "max": 1.0, "step": 0.01}),
                "blend": ("FLOAT", {"default": 0.88, "min": 0.0, "max": 1.0, "step": 0.01}),
                "preserve_luminance": ("FLOAT", {"default": 0.65, "min": 0.0, "max": 1.0, "step": 0.01}),
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE")
    RETURN_NAMES = ("image", "debug_overlay")
    FUNCTION = "normalize"
    CATEGORY = "VN/masks"

    def normalize(self, image, mask, target_r, target_g, target_b, blend, preserve_luminance):
        device = image.device
        img = image.float().clamp(0, 1)
        b, h, w, c = img.shape
        m = self._fit_mask(mask, b, h, w, device).clamp(0, 1).unsqueeze(-1)
        target = torch.tensor([float(target_r), float(target_g), float(target_b)], dtype=img.dtype, device=device)
        rgb = img[..., :3]
        lum = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]).unsqueeze(-1)
        target_lum = max(float(0.2126 * target[0] + 0.7152 * target[1] + 0.0722 * target[2]), 1e-4)
        # Preserve local rib/line shading without retaining old hue.
        scale = (lum / target_lum).clamp(0.55, 1.25)
        shaded = (target.view(1, 1, 1, 3) * (1.0 + (scale - 1.0) * float(preserve_luminance))).clamp(0, 1)
        out_rgb = rgb * (1.0 - m * float(blend)) + shaded * (m * float(blend))
        if c > 3:
            out = torch.cat([out_rgb, img[..., 3:]], dim=-1)
        else:
            out = out_rgb
        debug = out[..., :3].clone()
        debug = torch.where(m > 0.05, debug * 0.45 + torch.tensor([0.55, 0.0, 0.55], device=device), debug)
        return out.clamp(0, 1), debug.clamp(0, 1)


class VN_AutoHandFallbackProtectionMask(VN_AutoCollarCleanupMask):
    """Conservative bilateral hand-protection fallback for VN outfit edits.

    Florence hand prompts can return only one visible hand on front-facing VN
    sprites. This node keeps the existing Florence hand mask, then searches only
    the lower left/right side bands of the character silhouette for skin-tone
    hand-like pixels in the source image. It adds candidates only on a side whose
    existing hand-mask coverage is below a threshold, so it fails closed on sides
    Florence already captured.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "character_mask": ("MASK",),
                "existing_hand_mask": ("MASK",),
                "start_y_ratio": ("FLOAT", {"default": 0.62, "min": 0.30, "max": 0.95, "step": 0.01}),
                "end_y_ratio": ("FLOAT", {"default": 0.97, "min": 0.40, "max": 1.00, "step": 0.01}),
                "side_width_ratio": ("FLOAT", {"default": 0.42, "min": 0.10, "max": 0.60, "step": 0.01}),
                "min_existing_side_coverage": ("FLOAT", {"default": 0.004, "min": 0.0, "max": 0.10, "step": 0.001}),
                "skin_lum_min": ("FLOAT", {"default": 0.28, "min": 0.05, "max": 0.95, "step": 0.01}),
                "skin_lum_max": ("FLOAT", {"default": 0.88, "min": 0.10, "max": 1.00, "step": 0.01}),
                "skin_sat_min": ("FLOAT", {"default": 0.08, "min": 0.00, "max": 0.80, "step": 0.01}),
                "skin_sat_max": ("FLOAT", {"default": 0.50, "min": 0.05, "max": 1.00, "step": 0.01}),
                "red_over_green": ("FLOAT", {"default": 0.025, "min": -0.20, "max": 0.40, "step": 0.005}),
                "green_over_blue": ("FLOAT", {"default": 0.015, "min": -0.20, "max": 0.40, "step": 0.005}),
                "min_added_coverage": ("FLOAT", {"default": 0.00002, "min": 0.0, "max": 0.050, "step": 0.00002}),
                "max_added_coverage": ("FLOAT", {"default": 0.020, "min": 0.001, "max": 0.200, "step": 0.001}),
                "grow": ("INT", {"default": 4, "min": 0, "max": 64, "step": 1}),
                "blur": ("INT", {"default": 3, "min": 0, "max": 63, "step": 2}),
                "wrist_bridge_radius": ("INT", {"default": 42, "min": 0, "max": 128, "step": 1}),
                "wrist_bridge_grow": ("INT", {"default": 3, "min": 0, "max": 32, "step": 1}),
            }
        }

    RETURN_TYPES = ("MASK", "MASK", "MASK", "IMAGE", "FLOAT", "FLOAT", "MASK", "MASK", "MASK", "MASK")
    RETURN_NAMES = (
        "enhanced_hand_mask",
        "roi_mask",
        "added_mask",
        "debug_overlay",
        "left_existing_coverage",
        "right_existing_coverage",
        "refined_existing_mask",
        "skin_candidate_mask",
        "wrist_bridge_mask",
        "pretrim_hand_mask",
    )
    FUNCTION = "make_mask"
    CATEGORY = "VN/masks"

    def make_mask(
        self,
        image,
        character_mask,
        existing_hand_mask,
        start_y_ratio,
        end_y_ratio,
        side_width_ratio,
        min_existing_side_coverage,
        skin_lum_min,
        skin_lum_max,
        skin_sat_min,
        skin_sat_max,
        red_over_green,
        green_over_blue,
        min_added_coverage,
        max_added_coverage,
        grow,
        blur,
        wrist_bridge_radius,
        wrist_bridge_grow,
    ):
        device = image.device
        img = image.float().clamp(0, 1)
        b, h, w, c = img.shape
        char = self._fit_mask(character_mask, b, h, w, device) > 0.12
        existing = self._fit_mask(existing_hand_mask, b, h, w, device).clamp(0, 1)
        enhanced_list, roi_list, added_list, debug_list = [], [], [], []
        refined_existing_list, skin_candidate_list, wrist_bridge_list, pretrim_list = [], [], [], []
        left_covs, right_covs = [], []

        for i in range(b):
            im = img[i]
            cm = char[i]
            hm = existing[i]
            cb = self._bbox(cm, h, w)
            roi = torch.zeros((h, w), dtype=torch.bool, device=device)
            add_allowed = torch.zeros((h, w), dtype=torch.bool, device=device)
            spatial_prior = torch.zeros((h, w), dtype=torch.bool, device=device)
            left_cov = 0.0
            right_cov = 0.0

            if cb is not None:
                x1, y1, x2, y2 = cb
                char_w = max(x2 - x1 + 1, 1)
                char_h = max(y2 - y1 + 1, 1)
                side_w = max(1, int(char_w * side_width_ratio))
                y_start = min(h - 1, max(0, int(y1 + char_h * start_y_ratio)))
                y_end = min(h - 1, max(y_start, int(y1 + char_h * end_y_ratio)))
                left = torch.zeros((h, w), dtype=torch.bool, device=device)
                right = torch.zeros((h, w), dtype=torch.bool, device=device)
                left[y_start:y_end + 1, x1:min(x2 + 1, x1 + side_w)] = True
                right[y_start:y_end + 1, max(x1, x2 - side_w + 1):x2 + 1] = True
                # Restrict to character vicinity; allow a small dilation because hands
                # often touch the silhouette edge after outfit edits.
                char_near = self._dilate_bool(cm, 6)
                left = left & char_near
                right = right & char_near
                roi = left | right

                existing_bool = hm > 0.20
                left_area = max(float(left.float().sum().item()), 1.0)
                right_area = max(float(right.float().sum().item()), 1.0)
                left_cov = float((existing_bool & left).float().sum().item() / left_area)
                right_cov = float((existing_bool & right).float().sum().item() / right_area)
                center_x = (x1 + x2) // 2

                # If one side is captured and the opposite side is missing, mirror the
                # captured hand mask across the character center as a tight spatial
                # prior. This prevents broad cardigan/sleeve/pocket regions in the
                # lower-side ROI from being treated as skin fallback.
                def mirror_side(src_mask, dst_side):
                    mirrored = torch.zeros((h, w), dtype=torch.bool, device=device)
                    ys, xs = torch.where(src_mask)
                    if ys.numel() == 0:
                        return mirrored
                    mx = torch.clamp(2 * int(center_x) - xs, min=0, max=w - 1)
                    mirrored[ys, mx] = True
                    return self._dilate_bool(mirrored, 28) & dst_side & char_near

                if left_cov < float(min_existing_side_coverage):
                    add_allowed = add_allowed | left
                    spatial_prior = spatial_prior | mirror_side(existing_bool & right, left)
                if right_cov < float(min_existing_side_coverage):
                    add_allowed = add_allowed | right
                    spatial_prior = spatial_prior | mirror_side(existing_bool & left, right)

                if spatial_prior.any():
                    add_allowed = add_allowed & spatial_prior

            r, g, bl = im[..., 0], im[..., 1], im[..., 2]
            maxc = torch.maximum(torch.maximum(r, g), bl)
            minc = torch.minimum(torch.minimum(r, g), bl)
            sat = maxc - minc
            lum = 0.2126 * r + 0.7152 * g + 0.0722 * bl
            # v4e26: do not treat Florence hand masks as the final protection
            # mask. Florence often captures beige cardigan cuff/sleeve together
            # with the hand. Use it only as a spatial prior, then build a strict
            # lower-side terminal skin mask from the source image.
            yy = torch.arange(h, device=device).view(h, 1).expand(h, w)
            xx = torch.arange(w, device=device).view(1, w).expand(h, w)
            cb2 = self._bbox(cm, h, w)
            if cb2 is not None:
                x1b, y1b, x2b, y2b = cb2
                char_w2 = max(x2b - x1b + 1, 1)
                char_h2 = max(y2b - y1b + 1, 1)
                hand_floor = int(y1b + char_h2 * 0.84)
                lower_side_prior = roi & (yy >= hand_floor) & ((xx < x1b + char_w2 * 0.18) | (xx > x2b - char_w2 * 0.18))
            else:
                hand_floor = int(h * 0.84)
                lower_side_prior = roi & (yy >= hand_floor)

            strict_skin = (
                (lum > max(0.05, float(skin_lum_min) * 0.80))
                & (lum < min(0.98, float(skin_lum_max) * 1.04))
                & (sat > max(0.06, float(skin_sat_min) * 0.70))
                & (sat < min(0.95, float(skin_sat_max) * 1.15))
                & ((r - g) > max(0.035, float(red_over_green)))
                & ((r - bl) > 0.13)
                & ((g - bl) > -0.025)
                & roi
                & (yy >= hand_floor)
            )
            existing_seed = (hm > 0.20) & roi
            near_existing = self._dilate_bool(existing_seed, 18) & roi
            skin_seed = strict_skin & (existing_seed | near_existing | lower_side_prior)
            # Small close to reconnect finger line-art gaps; later component pass
            # trims terminal hand regions and rejects old cuff/sleeve columns.
            skin_seed = self._erode_bool(self._dilate_bool(skin_seed, 2), 2)
            terminal_skin = self._filter_hand_components(skin_seed, cm, hm > 0.20, roi, side_width_ratio)

            refined_existing_bool = terminal_skin & existing_seed
            refined_existing = refined_existing_bool.float()
            skin = terminal_skin

            # Wrist bridge is intentionally skin-only and terminal-region-only.
            # This keeps a little wrist if visible, but cannot preserve old fabric.
            bridge = torch.zeros((h, w), dtype=torch.bool, device=device)
            if wrist_bridge_radius and wrist_bridge_radius > 0 and skin.any():
                hand_near = self._dilate_bool(skin, min(int(wrist_bridge_radius), 18)) & roi & (yy >= hand_floor)
                bridge = strict_skin & hand_near
                bridge = self._filter_hand_components(bridge, cm, hm > 0.20, roi, side_width_ratio)
                if wrist_bridge_grow and wrist_bridge_grow > 0:
                    bridge = self._dilate_bool(bridge, min(int(wrist_bridge_grow), 1)) & roi & (yy >= hand_floor)

            combined_add = skin | bridge

            raw_area = float(combined_add.float().mean().item())
            if raw_area < float(min_added_coverage) or raw_area > float(max_added_coverage):
                added = torch.zeros((h, w), dtype=torch.float32, device=device)
            else:
                added_bool = combined_add
                if grow > 0:
                    added_bool = self._dilate_bool(added_bool, int(grow)) & roi
                added = added_bool.float()
                if blur and blur > 1:
                    added = self._blur_mask(added, int(blur))
                    added = (added * roi.float()).clamp(0, 1)

            pretrim = torch.maximum(refined_existing, added).clamp(0, 1)
            enhanced = self._trim_upper_cuff_from_hand_mask(pretrim, roi, cm, side_width_ratio)
            enhanced_list.append(enhanced)
            roi_list.append(roi.float())
            added_list.append(added)
            refined_existing_list.append(refined_existing.clamp(0, 1))
            skin_candidate_list.append(skin.float())
            wrist_bridge_list.append(bridge.float())
            pretrim_list.append(pretrim)
            left_covs.append(left_cov)
            right_covs.append(right_cov)
            debug_list.append(self._debug_overlay(im, roi.float(), combined_add.float(), added))

        return (
            torch.stack(enhanced_list, dim=0),
            torch.stack(roi_list, dim=0),
            torch.stack(added_list, dim=0),
            torch.stack(debug_list, dim=0),
            float(sum(left_covs) / max(len(left_covs), 1)),
            float(sum(right_covs) / max(len(right_covs), 1)),
            torch.stack(refined_existing_list, dim=0),
            torch.stack(skin_candidate_list, dim=0),
            torch.stack(wrist_bridge_list, dim=0),
            torch.stack(pretrim_list, dim=0),
        )

    def _trim_upper_cuff_from_hand_mask(self, mask, roi, char_mask, side_width_ratio):
        """Remove likely sleeve/cuff pixels from the top of lower-side hand blobs.

        Florence hand masks often include the shirt/cardigan cuff immediately
        above the hand. For outfit replacement we want original skin/fingers, not
        old cuff fabric. This trims only the upper band of compact lower-side
        components, leaving generated outfit cuffs visible.
        """
        if not bool((mask > 0.05).any().item()):
            return mask
        h, w = mask.shape
        cb = self._bbox(char_mask, h, w)
        if cb is None:
            return mask
        x1, y1, x2, y2 = cb
        char_w = max(x2 - x1 + 1, 1)
        side_w = max(1.0, char_w * float(side_width_ratio))
        center_x = (x1 + x2) / 2.0
        lower_y = y1 + (y2 - y1 + 1) * 0.52
        bin_cpu = ((mask > 0.05) & roi).detach().to("cpu").bool()
        out_cpu = mask.detach().to("cpu").clone()
        visited = torch.zeros_like(bin_cpu)
        ys, xs = torch.where(bin_cpu)
        for y0, x0 in zip(ys.tolist(), xs.tolist()):
            if visited[y0, x0]:
                continue
            stack = [(y0, x0)]
            visited[y0, x0] = True
            coords = []
            while stack:
                y, x = stack.pop()
                coords.append((y, x))
                for ny in (y - 1, y, y + 1):
                    for nx in (x - 1, x, x + 1):
                        if ny == y and nx == x:
                            continue
                        if 0 <= ny < h and 0 <= nx < w and (not visited[ny, nx]) and bin_cpu[ny, nx]:
                            visited[ny, nx] = True
                            stack.append((ny, nx))
            if len(coords) < 60:
                continue
            xs2 = [p[1] for p in coords]
            ys2 = [p[0] for p in coords]
            bx1, by1, bx2, by2 = min(xs2), min(ys2), max(xs2) + 1, max(ys2) + 1
            bw, bh = bx2 - bx1, by2 - by1
            cx = (bx1 + bx2) / 2.0
            cy = (by1 + by2) / 2.0
            near_side = (cx <= x1 + side_w * 0.75) or (cx >= x2 - side_w * 0.75)
            lower_side = cy >= lower_y and abs(cx - center_x) > char_w * 0.18
            if not (near_side and lower_side and bh >= 38 and bw <= max(180, char_w * 0.30)):
                continue
            trim = max(18, min(72, int(round(bh * 0.45))))
            cutoff = by1 + trim
            for y, x in coords:
                if y < cutoff:
                    out_cpu[y, x] = 0.0
        return out_cpu.to(mask.device).clamp(0, 1)

    def _filter_hand_components(self, candidate, char_mask, existing_hand, roi, side_width_ratio):
        """Keep only compact lower-side hand-like components.

        Skin-tone thresholding alone can catch cardigan/sleeve/shadow blobs when a
        hand is partly behind the skirt. This pass keeps plausible hand/finger
        components and rejects broad garment patches before grow/blur.
        """
        if not bool(candidate.any().item()):
            return candidate
        h, w = candidate.shape
        cb = self._bbox(char_mask, h, w)
        if cb is None:
            return candidate & False
        x1, y1, x2, y2 = cb
        char_w = max(x2 - x1 + 1, 1)
        char_h = max(y2 - y1 + 1, 1)
        center_x = (x1 + x2) / 2.0
        side_w = max(1.0, char_w * float(side_width_ratio))
        lower_y = y1 + char_h * 0.60
        max_area = max(26000, int(char_w * char_h * 0.025))
        min_area = 20

        cand_cpu = candidate.detach().to("cpu").bool()
        keep_cpu = torch.zeros_like(cand_cpu)
        visited = torch.zeros_like(cand_cpu)
        ys, xs = torch.where(cand_cpu)
        for y0, x0 in zip(ys.tolist(), xs.tolist()):
            if visited[y0, x0]:
                continue
            stack = [(y0, x0)]
            visited[y0, x0] = True
            coords = []
            while stack:
                y, x = stack.pop()
                coords.append((y, x))
                for ny in (y - 1, y, y + 1):
                    for nx in (x - 1, x, x + 1):
                        if ny == y and nx == x:
                            continue
                        if 0 <= ny < h and 0 <= nx < w and (not visited[ny, nx]) and cand_cpu[ny, nx]:
                            visited[ny, nx] = True
                            stack.append((ny, nx))
            area = len(coords)
            if area < min_area or area > max_area:
                continue
            xs2 = [p[1] for p in coords]
            ys2 = [p[0] for p in coords]
            bx1, by1, bx2, by2 = min(xs2), min(ys2), max(xs2) + 1, max(ys2) + 1
            bw, bh = bx2 - bx1, by2 - by1
            cx = (bx1 + bx2) / 2.0
            cy = (by1 + by2) / 2.0
            side_dist = abs(cx - center_x)
            near_side = (cx <= x1 + side_w * 0.62) or (cx >= x2 - side_w * 0.62)
            plausible_box = (3 <= bw <= max(180, char_w * 0.34)) and (4 <= bh <= max(700, char_h * 0.46))
            lower_side = cy >= lower_y and near_side and side_dist > char_w * 0.20
            if lower_side and plausible_box:
                trim_top = max(by1, by2 - int(min(95, max(38, bh * 0.38))))
                for y, x in coords:
                    outer_terminal = (x <= x1 + char_w * 0.22) or (x >= x2 - char_w * 0.22)
                    if y >= trim_top and outer_terminal:
                        keep_cpu[y, x] = True
        keep = keep_cpu.to(candidate.device)
        # Preserve any existing Florence hand pixels; this method only filters
        # fallback additions, so returning empty is safe and fail-closed.
        return keep & roi


class VN_AutoOutfitSilhouetteProtectMask(VN_AutoCollarCleanupMask):
    """Protect lower-side silhouette/rim to prevent 06 outfit inpaint shrink.

    Use as an additional protection mask subtracted from the outfit edit mask.
    It creates a narrow outside/inside rim around the original character mask on
    the lower sides plus an optional lower-thigh preserve region. This is for 06
    opaque-source stabilization, not 03 alpha cleanup.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "character_mask": ("MASK",),
                "existing_protect_mask": ("MASK",),
                "lower_start_y_ratio": ("FLOAT", {"default": 0.48, "min": 0.20, "max": 0.95, "step": 0.01}),
                "side_width_ratio": ("FLOAT", {"default": 0.28, "min": 0.05, "max": 0.50, "step": 0.01}),
                "rim_radius": ("INT", {"default": 8, "min": 1, "max": 64, "step": 1}),
                "thigh_start_y_ratio": ("FLOAT", {"default": 0.80, "min": 0.50, "max": 1.00, "step": 0.01}),
                "thigh_width_ratio": ("FLOAT", {"default": 0.34, "min": 0.05, "max": 0.80, "step": 0.01}),
                "blur": ("INT", {"default": 3, "min": 0, "max": 63, "step": 2}),
            }
        }

    RETURN_TYPES = ("MASK", "MASK", "MASK", "IMAGE", "FLOAT")
    RETURN_NAMES = ("protect_mask", "rim_mask", "thigh_mask", "debug_overlay", "coverage")
    FUNCTION = "make_mask"
    CATEGORY = "VN/masks"

    def make_mask(self, image, character_mask, existing_protect_mask, lower_start_y_ratio, side_width_ratio, rim_radius, thigh_start_y_ratio, thigh_width_ratio, blur):
        device = image.device
        img = image.float().clamp(0, 1)
        b, h, w, c = img.shape
        char = self._fit_mask(character_mask, b, h, w, device) > 0.12
        existing = self._fit_mask(existing_protect_mask, b, h, w, device) > 0.05
        protect_list, rim_list, thigh_list, debug_list, cov_values = [], [], [], [], []
        for i in range(b):
            im = img[i]
            cm = char[i]
            em = existing[i]
            cb = self._bbox(cm, h, w)
            if cb is None:
                rim = torch.zeros((h, w), dtype=torch.bool, device=device)
                thigh = torch.zeros((h, w), dtype=torch.bool, device=device)
            else:
                x1, y1, x2, y2 = cb
                char_w = max(x2 - x1 + 1, 1)
                char_h = max(y2 - y1 + 1, 1)
                center_x = (x1 + x2) // 2
                lower_y = int(y1 + char_h * float(lower_start_y_ratio))
                side_w = int(char_w * float(side_width_ratio))
                dil = self._dilate_bool(cm, int(rim_radius))
                ero = self._erode_bool(cm, max(1, int(rim_radius) // 2))
                ring = dil & (~ero)
                side_roi = torch.zeros((h, w), dtype=torch.bool, device=device)
                side_roi[lower_y:y2 + 1, x1:min(x2 + 1, x1 + side_w)] = True
                side_roi[lower_y:y2 + 1, max(x1, x2 - side_w + 1):x2 + 1] = True
                rim = ring & side_roi

                thigh_y = int(y1 + char_h * float(thigh_start_y_ratio))
                thigh_half = int(char_w * float(thigh_width_ratio) / 2)
                thigh = torch.zeros((h, w), dtype=torch.bool, device=device)
                thigh[thigh_y:y2 + 1, max(x1, center_x - thigh_half):min(x2 + 1, center_x + thigh_half)] = True
                thigh = thigh & cm
            protect = (rim | thigh) & (~em)
            protect_f = protect.float()
            if blur and blur > 1:
                protect_f = self._blur_mask(protect_f, int(blur))
            protect_list.append(protect_f.clamp(0, 1))
            rim_list.append(rim.float())
            thigh_list.append(thigh.float())
            cov_values.append(float(protect_f.mean().item()))
            debug = im.clone()
            debug = torch.where(rim.unsqueeze(-1), debug * 0.35 + torch.tensor([0.0, 0.35, 0.80], device=device), debug)
            debug = torch.where(thigh.unsqueeze(-1), debug * 0.55 + torch.tensor([0.65, 0.15, 0.0], device=device), debug)
            debug = torch.where(protect_f.unsqueeze(-1) > 0.05, debug * 0.70 + torch.tensor([0.0, 0.25, 0.0], device=device), debug)
            debug_list.append(debug.clamp(0, 1))
        return (
            torch.stack(protect_list, dim=0),
            torch.stack(rim_list, dim=0),
            torch.stack(thigh_list, dim=0),
            torch.stack(debug_list, dim=0),
            float(sum(cov_values) / max(len(cov_values), 1)),
        )


class VN_AutoLowerSideResidueMask(VN_AutoCollarCleanupMask):
    """Fail-closed mask for lower-side bright hand/sleeve residue after outfit edits.

    Designed for VN 06 outfit outputs before alpha conversion. It searches only
    the lower left/right side bands of the character bbox for bright low-sat
    fragments (white glove/sleeve-like remnants), rejects broad masks, then
    grows/blurs the accepted candidate for a background-fill or local inpaint.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "character_mask": ("MASK",),
                "start_y_ratio": ("FLOAT", {"default": 0.76, "min": 0.40, "max": 0.95, "step": 0.01}),
                "side_width_ratio": ("FLOAT", {"default": 0.34, "min": 0.10, "max": 0.50, "step": 0.01}),
                "lum_min": ("FLOAT", {"default": 0.82, "min": 0.40, "max": 0.99, "step": 0.01}),
                "sat_max": ("FLOAT", {"default": 0.20, "min": 0.02, "max": 0.60, "step": 0.01}),
                "min_coverage": ("FLOAT", {"default": 0.00005, "min": 0.0, "max": 0.050, "step": 0.00005}),
                "max_coverage": ("FLOAT", {"default": 0.018, "min": 0.001, "max": 0.200, "step": 0.001}),
                "grow": ("INT", {"default": 3, "min": 0, "max": 64, "step": 1}),
                "blur": ("INT", {"default": 3, "min": 0, "max": 63, "step": 2}),
            }
        }

    RETURN_TYPES = ("MASK", "MASK", "MASK", "IMAGE", "FLOAT")
    RETURN_NAMES = ("cleanup_mask", "roi_mask", "candidate_mask", "debug_overlay", "coverage")
    FUNCTION = "make_mask"
    CATEGORY = "VN/masks"

    def make_mask(self, image, character_mask, start_y_ratio, side_width_ratio, lum_min, sat_max, min_coverage, max_coverage, grow, blur):
        device = image.device
        img = image.float().clamp(0, 1)
        b, h, w, c = img.shape
        char = self._fit_mask(character_mask, b, h, w, device) > 0.12
        cleanup_list, roi_list, cand_list, debug_list, cov_values = [], [], [], [], []
        for i in range(b):
            im = img[i]
            cm = char[i]
            cb = self._bbox(cm, h, w)
            if cb is None:
                roi = torch.zeros((h, w), dtype=torch.bool, device=device)
            else:
                x1, y1, x2, y2 = cb
                char_w = max(x2 - x1 + 1, 1)
                side_w = max(1, int(char_w * side_width_ratio))
                y_start = min(h - 1, max(0, int(y1 + (y2 - y1 + 1) * start_y_ratio)))
                roi = torch.zeros((h, w), dtype=torch.bool, device=device)
                roi[y_start:y2 + 1, x1:min(x2 + 1, x1 + side_w)] = True
                roi[y_start:y2 + 1, max(x1, x2 - side_w + 1):x2 + 1] = True
                roi = roi & self._dilate_bool(cm, 8)
            r, g, bl = im[..., 0], im[..., 1], im[..., 2]
            maxc = torch.maximum(torch.maximum(r, g), bl)
            minc = torch.minimum(torch.minimum(r, g), bl)
            sat = maxc - minc
            lum = 0.2126 * r + 0.7152 * g + 0.0722 * bl
            candidate = (lum > lum_min) & (sat < sat_max) & roi
            raw_area = float(candidate.float().mean().item())
            roi_area = max(float(roi.float().mean().item()), 1e-8)
            if raw_area < min_coverage or raw_area > max_coverage or (raw_area / roi_area) > 0.45:
                clean = torch.zeros((h, w), dtype=torch.float32, device=device)
            else:
                clean_bool = candidate
                if grow > 0:
                    clean_bool = self._dilate_bool(clean_bool, grow)
                clean = clean_bool.float()
                if blur and blur > 1:
                    clean = self._blur_mask(clean, blur)
            cleanup_list.append(clean)
            roi_list.append(roi.float())
            cand_list.append(candidate.float())
            cov_values.append(float(clean.mean().item()))
            debug_list.append(self._debug_overlay(im, roi.float(), candidate.float(), clean))
        return (
            torch.stack(cleanup_list, dim=0),
            torch.stack(roi_list, dim=0),
            torch.stack(cand_list, dim=0),
            torch.stack(debug_list, dim=0),
            float(sum(cov_values) / max(len(cov_values), 1)),
        )


class VN_OutfitForegroundResidueCut(VN_AutoCollarCleanupMask):
    """Fail-closed foreground/composite residue cutter for VN 06 outfit results.

    Unlike a pure alpha post-pass, this node receives the source character mask,
    final edit mask, and final face/hair/hand protection mask. It removes only
    background-like pixels that are either border-connected or lie in dynamic
    neck/side residue ROIs inside the editable outfit area. Protected face, hair,
    and hands are never cut. This targets the v4e12 failure mode: regenerated
    outfits that are narrower than the original sprite leave old hood/collar or
    sleeve-shaped grey foreground islands before the final alpha workflow.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "character_mask": ("MASK",),
                "edit_mask": ("MASK",),
                "protect_mask": ("MASK",),
                "bg_distance": ("FLOAT", {"default": 0.18, "min": 0.01, "max": 1.00, "step": 0.01}),
                "sat_max": ("FLOAT", {"default": 0.16, "min": 0.01, "max": 1.00, "step": 0.01}),
                "lum_min": ("FLOAT", {"default": 0.22, "min": 0.00, "max": 1.00, "step": 0.01}),
                "lum_max": ("FLOAT", {"default": 0.86, "min": 0.00, "max": 1.00, "step": 0.01}),
                "bridge_radius": ("INT", {"default": 1, "min": 0, "max": 8, "step": 1}),
                "protect_expand": ("INT", {"default": 6, "min": 0, "max": 48, "step": 1}),
                "side_width_ratio": ("FLOAT", {"default": 0.22, "min": 0.05, "max": 0.60, "step": 0.01}),
                "side_start_y_ratio": ("FLOAT", {"default": 0.24, "min": 0.00, "max": 0.95, "step": 0.01}),
                "neck_top_pad": ("INT", {"default": 26, "min": -128, "max": 256, "step": 1}),
                "neck_height": ("INT", {"default": 170, "min": 32, "max": 640, "step": 1}),
                "neck_width_ratio": ("FLOAT", {"default": 0.46, "min": 0.10, "max": 1.00, "step": 0.01}),
                "residue_strength": ("FLOAT", {"default": 1.35, "min": 1.00, "max": 4.00, "step": 0.05}),
                "max_removed_coverage": ("FLOAT", {"default": 0.72, "min": 0.01, "max": 0.95, "step": 0.01}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "MASK", "IMAGE", "FLOAT")
    RETURN_NAMES = ("rgba_image", "cut_mask", "residue_roi", "debug_overlay", "removed_coverage")
    FUNCTION = "cut_residue"
    CATEGORY = "VN/masks"

    def cut_residue(self, image, character_mask, edit_mask, protect_mask, bg_distance, sat_max, lum_min, lum_max, bridge_radius, protect_expand, side_width_ratio, side_start_y_ratio, neck_top_pad, neck_height, neck_width_ratio, residue_strength, max_removed_coverage):
        device = image.device
        img = image.float().clamp(0, 1)
        b, h, w, c = img.shape
        rgb = img[..., :3]
        alpha_in = img[..., 3:4] if c >= 4 else torch.ones((b, h, w, 1), dtype=img.dtype, device=device)
        char = self._fit_mask(character_mask, b, h, w, device) > 0.12
        edit = self._fit_mask(edit_mask, b, h, w, device) > 0.04
        prot = self._fit_mask(protect_mask, b, h, w, device) > 0.05

        rgba_list, cut_list, roi_list, debug_list, cov_values = [], [], [], [], []
        for i in range(b):
            im = rgb[i]
            cm = char[i]
            em = edit[i]
            pm = prot[i]
            patch = max(1, min(80, h // 8, w // 8))
            corners = torch.cat([
                im[:patch, :patch].reshape(-1, 3),
                im[:patch, w - patch:w].reshape(-1, 3),
                im[h - patch:h, :patch].reshape(-1, 3),
                im[h - patch:h, w - patch:w].reshape(-1, 3),
            ], dim=0)
            bg = corners.median(dim=0).values
            maxc = im.max(dim=-1).values
            minc = im.min(dim=-1).values
            sat = maxc - minc
            lum = 0.2126 * im[..., 0] + 0.7152 * im[..., 1] + 0.0722 * im[..., 2]
            dist = torch.sqrt(((im - bg) ** 2).sum(dim=-1).clamp_min(0.0))

            bg_like = (dist < float(bg_distance)) & (sat < float(sat_max)) & (lum > float(lum_min)) & (lum < float(lum_max))
            if bridge_radius > 0:
                bg_like = self._dilate_bool(bg_like, int(bridge_radius)) & ((sat < float(sat_max) * 1.35) & (lum > float(lum_min)) & (lum < float(lum_max)))
            border = torch.zeros((h, w), dtype=torch.bool, device=device)
            border[0, :] = True; border[h - 1, :] = True; border[:, 0] = True; border[:, w - 1] = True
            border_cut = self._border_connected(bg_like, border)

            cb = self._bbox(cm, h, w)
            pb = self._bbox(pm, h, w) or cb
            side_roi = torch.zeros((h, w), dtype=torch.bool, device=device)
            neck_roi = torch.zeros((h, w), dtype=torch.bool, device=device)
            if cb is not None:
                x1, y1, x2, y2 = cb
                char_w = max(x2 - x1 + 1, 1)
                char_h = max(y2 - y1 + 1, 1)
                side_w = max(1, int(char_w * float(side_width_ratio)))
                y0 = int(y1 + char_h * float(side_start_y_ratio))
                side_roi[y0:y2 + 1, x1:min(x2 + 1, x1 + side_w)] = True
                side_roi[y0:y2 + 1, max(x1, x2 - side_w + 1):x2 + 1] = True
                if pb is not None:
                    px1, py1, px2, py2 = pb
                    center_x = (x1 + x2) // 2
                    half_w = int(char_w * float(neck_width_ratio) / 2)
                    ny1 = max(y1, int(py2) - int(neck_top_pad))
                    ny2 = min(y2, ny1 + int(neck_height))
                    neck_roi[ny1:ny2 + 1, max(x1, center_x - half_w):min(x2 + 1, center_x + half_w)] = True

            protected = self._dilate_bool(pm, int(protect_expand)) if protect_expand > 0 else pm
            residue_roi = (side_roi | neck_roi) & cm & em & (~protected)
            strong = float(residue_strength)
            neutral_residue = (dist < float(bg_distance) * strong) & (sat < float(sat_max) * 1.25) & (lum > float(lum_min) * 0.85) & (lum < float(lum_max) * 0.92)
            # Cut only residue connected to the flat background. This avoids
            # punching holes through real low-saturation jacket folds/highlights
            # inside the regenerated sleeve/body.
            residue_connected = self._border_connected(bg_like | neutral_residue, border)
            residue_cut = residue_connected & residue_roi
            cut = border_cut | residue_cut

            cov = float(cut.float().mean().item())
            if cov > float(max_removed_coverage):
                cut = torch.zeros((h, w), dtype=torch.bool, device=device)
                cov = 0.0
            a = alpha_in[i, ..., 0].clone()
            a = torch.where(cut, torch.zeros_like(a), a)
            rgba = torch.cat([im, a.unsqueeze(-1)], dim=-1).clamp(0, 1)
            debug = im.clone()
            debug = torch.where(residue_roi.unsqueeze(-1), debug * 0.78 + torch.tensor([0.0, 0.0, 0.22], device=device), debug)
            debug = torch.where(cut.unsqueeze(-1), debug * 0.28 + torch.tensor([0.0, 0.72, 0.0], device=device), debug)
            rgba_list.append(rgba)
            cut_list.append(cut.float())
            roi_list.append(residue_roi.float())
            debug_list.append(debug.clamp(0, 1))
            cov_values.append(cov)
        return torch.stack(rgba_list, dim=0), torch.stack(cut_list, dim=0), torch.stack(roi_list, dim=0), torch.stack(debug_list, dim=0), float(sum(cov_values) / max(len(cov_values), 1))

    def _border_connected(self, mask_bool, border_bool):
        cur = mask_bool & border_bool
        if not bool(cur.any().item()):
            return cur
        for _ in range(mask_bool.shape[0] + mask_bool.shape[1]):
            nxt = self._dilate_bool(cur, 1) & mask_bool
            if bool(torch.equal(nxt, cur)):
                return cur
            cur = nxt
        return cur

