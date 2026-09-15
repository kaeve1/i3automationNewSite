/* Service exploration and project brief preparation run entirely in the browser. */
document.querySelectorAll('[data-service-picker]').forEach(picker=>{
  const tabs=Array.from(picker.querySelectorAll('[role="tab"]'));
  function select(tab,focus=false){
    tabs.forEach(item=>{
      const active=item===tab;
      item.setAttribute('aria-selected',String(active));
      item.tabIndex=active?0:-1;
      document.getElementById(item.getAttribute('aria-controls')).hidden=!active;
    });
    if(focus)tab.focus();
  }
  tabs.forEach((tab,i)=>{
    tab.addEventListener('click',()=>select(tab));
    tab.addEventListener('keydown',event=>{
      let next;
      if(event.key==='ArrowDown'||event.key==='ArrowRight')next=(i+1)%tabs.length;
      if(event.key==='ArrowUp'||event.key==='ArrowLeft')next=(i+tabs.length-1)%tabs.length;
      if(event.key==='Home')next=0;
      if(event.key==='End')next=tabs.length-1;
      if(next!==undefined){event.preventDefault();select(tabs[next],true);}
    });
  });
});
document.querySelectorAll('.scope-builder').forEach(builder=>{
  const inputs=Array.from(builder.querySelectorAll('input[type="checkbox"]'));
  const summary=builder.querySelector('[data-scope-summary]');
  const email=builder.querySelector('[data-scope-email]');
  function update(){
    const selected=inputs.filter(input=>input.checked).map(input=>input.value);
    summary.textContent=selected.length?'I would like to discuss: '+selected.join('; ')+'.':'Select the areas relevant to your project, or start with a general question.';
    const body='Hello i3 team,\n\nI would like to discuss '+(selected.length?selected.join(', '):'a controls project')+'.\n\nSite location: \nCurrent platforms: \nProject timing: \nProject description: \n\nThank you.';
    email.href='mailto:acastro@i3automations.com?subject='+encodeURIComponent('Project scope')+'&body='+encodeURIComponent(body);
  }
  inputs.forEach(input=>input.addEventListener('change',update));
  update();
});
