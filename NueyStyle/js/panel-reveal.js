/* Scroll-linked pixel cover. Thresholds come from the user's original i3 design.
   Only active while visible; transform/opacity are written on individual tiles. */
(() => {
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const panels = [...document.querySelectorAll('.cobertura')].map(section => ({
    section, tiles:[...section.querySelectorAll('.cobertura__grade > i')],
    lines:[...section.querySelectorAll('.cobertura__frase > span')],
    label:section.querySelector('.cobertura__legenda')
  }));
  if(!panels.length) return;
  const clamp = value => Math.max(0,Math.min(1,value));
  let frame=0;
  const paint = () => {
    frame=0;
    if(motion.matches) return;
    const viewport=innerHeight;
    const measurements=panels.map(panel=>({panel,rect:panel.section.getBoundingClientRect()}));
    measurements.forEach(({panel,rect})=>{
      if(rect.bottom < 0 || rect.top > viewport) return;
      const progress=clamp(-rect.top/Math.max(1,rect.height-viewport));
      panel.tiles.forEach(tile=>{
        const phase=clamp((progress-Number(tile.style.getPropertyValue('--o'))*.72)*8);
        tile.style.transform=`scale(${Math.max(.001,phase)})`;
        tile.style.opacity=phase>0 ? '1':'0';
      });
      panel.lines.forEach((line,index)=>{
        const phase=clamp((progress-(index===0?.78:.86))*10);
        line.style.opacity=String(phase);
        line.style.transform=`translateY(${(1-phase)*(index===0?18:26)}px)`;
      });
      if(panel.label) panel.label.style.opacity=String(clamp((.78-progress)*6.25));
    });
  };
  const schedule=()=>{if(!frame && !motion.matches) frame=requestAnimationFrame(paint)};
  const configure=()=>{panels.forEach(({section})=>section.classList.toggle('is-animated',!motion.matches));schedule()};
  addEventListener('scroll',schedule,{passive:true});
  addEventListener('resize',schedule,{passive:true});
  addEventListener('pageshow',schedule);
  motion.addEventListener('change',configure);
  configure();
})();
