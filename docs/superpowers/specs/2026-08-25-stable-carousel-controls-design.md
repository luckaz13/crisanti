# Stable Carousel Controls — Design

## Objective

Prevent carousel navigation arrows from moving vertically when consecutive artwork images have different heights, avoiding missed clicks during repeated navigation.

## Root cause

Desktop controls are absolutely positioned with `top: 50%` relative to `.gallery-carousel`. JavaScript changes `.gallery-viewport` height to match every active figure, so the carousel height and its 50% midpoint move after each navigation.

## Selected behavior

- On desktop, each carousel captures the vertical center of its first measurable slide and stores that value as its control anchor.
- Changing slides may continue to resize the viewport, but must not change the stored control anchor.
- A real change in carousel width invalidates and recalculates the anchor, preserving correct positioning after responsive layout changes.
- Hidden tab panels defer measurement until they become visible.
- Mobile behavior at widths up to 768px remains unchanged: controls stay in normal flow above the image.

## Implementation boundary

- JavaScript owns measurement and exposes the anchor through a carousel-scoped CSS custom property.
- CSS consumes the custom property for the desktop `top` position and retains its current mobile override.
- No gallery markup, image sizing, captions, autoplay, swipe behavior, or navigation semantics change.

## Verification

- A regression test must fail before implementation when the stable-anchor behavior is absent.
- Browser verification must compare arrow coordinates before and after navigating between slides with different heights.
- Existing acervo tests and reference audit must continue to pass.
- Desktop and mobile layouts must be checked independently.
