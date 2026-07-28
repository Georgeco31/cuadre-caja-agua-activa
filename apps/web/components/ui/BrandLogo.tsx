"use client";

import { useState } from "react";

type BrandLogoProps = {
  className?: string;
  variant: "full" | "icon";
};

const brandAssets = {
  full: {
    height: 739,
    src: "/brand/logo-horizontal.png",
    width: 1105,
  },
  icon: {
    height: 1435,
    src: "/brand/logo-icon.png",
    width: 1080,
  },
} as const;

export function BrandLogo({ className = "", variant }: BrandLogoProps) {
  const [hasLoadError, setHasLoadError] = useState(false);
  const asset = brandAssets[variant];

  if (hasLoadError) {
    return (
      <span
        aria-label="Agua Activa"
        className={`inline-flex items-center justify-center text-center font-semibold text-water-800 ${
          variant === "icon" ? "text-[8px] leading-tight" : "text-sm"
        } ${className}`}
        role="img"
      >
        Agua Activa ERP
      </span>
    );
  }

  return (
    <img
      alt="Agua Activa"
      className={`object-contain ${className}`}
      height={asset.height}
      onError={() => setHasLoadError(true)}
      src={asset.src}
      width={asset.width}
    />
  );
}
