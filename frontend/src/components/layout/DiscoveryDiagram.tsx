import { useEffect, useId, useRef } from 'react'
import gsap from 'gsap'

export function DiscoveryDiagram() {
  const root = useRef<HTMLDivElement>(null)
  const id = useId().replaceAll(':', '')
  const maskId = `route-mask-${id}`

  useEffect(() => {
    const media = gsap.matchMedia()
    media.add('(min-width: 768px) and (prefers-reduced-motion: no-preference)', () => {
      const svg = root.current?.querySelector('svg')
      if (!svg) return
      const pin = svg.querySelector('.pin-motion')
      const mask = svg.querySelector<SVGPathElement>('.route-mask')!
      const mark = svg.querySelector('.saved-motion')
      const check = svg.querySelector<SVGPathElement>('.saved-check')!
      const halo = svg.querySelector('.pin-halo')
      const labels = svg.querySelectorAll('.stage-label')
      const length = mask.getTotalLength()
      const checkLength = check.getTotalLength()
      // Draw a solid mask over the original dashed route, preserving its design.
      gsap.timeline({ delay: 0.25, defaults: { ease: 'power2.out' } })
        .fromTo(pin, { y: -10, opacity: 0.35 }, { y: 0, opacity: 1, duration: 0.5 }, 0)
        .fromTo(halo, { attr: { r: 26 }, opacity: 0 }, { attr: { r: 40 }, opacity: 0.4, duration: 0.45 }, 0.2)
        .to(halo, { opacity: 0, duration: 0.4 }, 0.65)
        .fromTo(labels[0], { opacity: 0.35 }, { opacity: 1, duration: 0.3 }, 0.2)
        .fromTo(mask, { strokeDasharray: length, strokeDashoffset: length }, { strokeDashoffset: 0, duration: 1.2, ease: 'power1.inOut' }, 0.55)
        .fromTo(mark, { scale: 0.88, opacity: 0.35 }, { scale: 1, opacity: 1, duration: 0.4, transformOrigin: '50% 50%' }, 1.6)
        .fromTo(check, { strokeDasharray: checkLength, strokeDashoffset: checkLength }, { strokeDashoffset: 0, duration: 0.35 }, 1.9)
        .fromTo(labels[1], { opacity: 0.35 }, { opacity: 1, duration: 0.3 }, 2)

    }, root)
    return () => media.revert()
  }, [])

  return (<div className="discovery-illustration" ref={root}>
    <svg className="map" viewBox="0 0 480 300" width="480" height="300" role="img" aria-labelledby={`map-title-${id} map-desc-${id}`}>
    <title id={`map-title-${id}`}>From discovery to opportunity</title>
    <desc id={`map-desc-${id}`}>An illustrative street map connects a business pin to a saved opportunity. No real business data is shown.</desc>
    <defs><mask id={maskId} maskUnits="userSpaceOnUse" x="96" y="84" width="260" height="120">
      <path className="route-mask" d="M112 112v58q0 16 16 16h94q16 0 16-16v-58q0-16 16-16h75" fill="none" stroke="white" strokeWidth="6" />
    </mask></defs>
<g fill="none" stroke="#FAF8F2" strokeOpacity=".15" strokeWidth="1"><path d="M0 44h480M0 128h480M0 212h480M64 0v264M176 0v264M288 0v264M400 0v264"></path><path d="m0 242 480-148M130 0l170 264" strokeWidth="16" stroke="#344C40"></path><path d="m0 242 480-148M130 0l170 264"></path></g>
<g fill="#FAF8F2" fillOpacity=".04" stroke="#FAF8F2" strokeOpacity=".2"><rect x="80" y="60" width="72" height="48" rx="4"></rect><rect x="304" y="144" width="72" height="48" rx="4"></rect><rect x="304" y="60" width="72" height="48" rx="4"></rect><rect x="80" y="144" width="72" height="48" rx="4"></rect></g>
<path id="map-route" mask={`url(#${maskId})`} d="M112 112v58q0 16 16 16h94q16 0 16-16v-58q0-16 16-16h75" fill="none" stroke="#FAF8F2" strokeOpacity=".7" strokeWidth="1.5" strokeDasharray="4 6"></path>
<g transform="translate(112 84)"><g className="pin-motion"><circle className="pin-halo" cx="0" cy="4" r="26" fill="none" stroke="#FAF8F2" strokeWidth="1" opacity="0" /><path d="M0 32S-22 12-22-2a22 22 0 0 1 44 0C22 12 0 32 0 32Z" fill="#C43D2B" stroke="#FAF8F2" strokeWidth="1.5"></path><path d="M-8 5V-8H8V5M-11-8h22M-3 5v-7h6v7" fill="none" stroke="#FAF8F2" strokeWidth="1.5"></path></g></g>
<g transform="translate(336 96)"><g className="saved-motion"><circle r="23" fill="#344C40" stroke="#FAF8F2" strokeWidth="1.5"></circle><path className="saved-check" d="m-8 0 5 5L9-7" fill="none" stroke="#FAF8F2" strokeWidth="1.6"></path></g></g>
<g fill="#FAF8F2" fontFamily="DM Sans,sans-serif" fontSize="11"><text className="stage-label" x="72" y="160">Discover</text><text className="stage-label" x="304" y="144">Opportunity saved</text></g><text x="0" y="292" fill="#FAF8F2" fillOpacity=".75" fontFamily="DM Sans,sans-serif" fontSize="10" letterSpacing="1.6">AN ILLUSTRATION OF WHAT’S NEXT</text></svg>
  </div>)
}
