"""
ComfyUI-VN-AutoMasks

Small deterministic mask helpers for VN asset workflows.
"""

from .nodes import (
    VN_AutoCollarCleanupMask,
    VN_AutoHandFallbackProtectionMask,
    VN_AutoLowerSideResidueMask,
    VN_AutoMaskedColorNormalize,
    VN_AutoOutfitSilhouetteProtectMask,
    VN_AutoTrimCleanupMask,
    VN_AlphaEdgeRefine,
    VN_OutfitForegroundResidueCut,
)

NODE_CLASS_MAPPINGS = {
    "VN_AutoCollarCleanupMask": VN_AutoCollarCleanupMask,
    "VN_AutoHandFallbackProtectionMask": VN_AutoHandFallbackProtectionMask,
    "VN_AutoLowerSideResidueMask": VN_AutoLowerSideResidueMask,
    "VN_AutoMaskedColorNormalize": VN_AutoMaskedColorNormalize,
    "VN_AutoOutfitSilhouetteProtectMask": VN_AutoOutfitSilhouetteProtectMask,
    "VN_AutoTrimCleanupMask": VN_AutoTrimCleanupMask,
    "VN_AlphaEdgeRefine": VN_AlphaEdgeRefine,
    "VN_OutfitForegroundResidueCut": VN_OutfitForegroundResidueCut,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VN_AutoCollarCleanupMask": "VN Auto Collar Cleanup Mask",
    "VN_AutoHandFallbackProtectionMask": "VN Auto Hand Fallback Protection Mask",
    "VN_AutoLowerSideResidueMask": "VN Auto Lower-Side Residue Mask",
    "VN_AutoMaskedColorNormalize": "VN Auto Masked Color Normalize",
    "VN_AutoOutfitSilhouetteProtectMask": "VN Auto Outfit Silhouette Protect Mask",
    "VN_AutoTrimCleanupMask": "VN Auto Trim Cleanup Mask",
    "VN_AlphaEdgeRefine": "VN Alpha Edge Refine",
    "VN_OutfitForegroundResidueCut": "VN Outfit Foreground Residue Cut",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
