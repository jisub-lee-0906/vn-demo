"""
ComfyUI-VN-AutoMasks

Small deterministic mask helpers for VN asset workflows.
"""

from .nodes import (
    VN_AutoCollarCleanupMask,
    VN_AutoHandFallbackProtectionMask,
    VN_AutoLowerSideResidueMask,
    VN_AutoOutfitSilhouetteProtectMask,
    VN_AlphaEdgeRefine,
)

NODE_CLASS_MAPPINGS = {
    "VN_AutoCollarCleanupMask": VN_AutoCollarCleanupMask,
    "VN_AutoHandFallbackProtectionMask": VN_AutoHandFallbackProtectionMask,
    "VN_AutoLowerSideResidueMask": VN_AutoLowerSideResidueMask,
    "VN_AutoOutfitSilhouetteProtectMask": VN_AutoOutfitSilhouetteProtectMask,
    "VN_AlphaEdgeRefine": VN_AlphaEdgeRefine,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VN_AutoCollarCleanupMask": "VN Auto Collar Cleanup Mask",
    "VN_AutoHandFallbackProtectionMask": "VN Auto Hand Fallback Protection Mask",
    "VN_AutoLowerSideResidueMask": "VN Auto Lower-Side Residue Mask",
    "VN_AutoOutfitSilhouetteProtectMask": "VN Auto Outfit Silhouette Protect Mask",
    "VN_AlphaEdgeRefine": "VN Alpha Edge Refine",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
