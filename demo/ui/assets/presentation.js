/* Presentation only: no ballot, encryption, authentication or proof handlers. */
(() => {
  if (document.querySelector('#banner')) {
    const heading = document.querySelector('#banner > div');
    if (heading && heading.firstChild?.nodeType === Node.TEXT_NODE) heading.firstChild.textContent = '✓  verifiable vote / Voting booth';
    const observer = new MutationObserver(() => {
      document.querySelectorAll('#questions_div button').forEach(button => {if(button.textContent === 'Start') button.textContent = 'Begin your ballot →';});
      const proceed = document.querySelector('#proceed_button');
      if (proceed && proceed.textContent === 'Proceed to Login') proceed.textContent = 'Continue to authentication →';
    });
    observer.observe(document.querySelector('#content'), {childList:true, subtree:true});
  }
  const copy = document.querySelector('[data-copy-tracker]');
  if(copy) copy.addEventListener('click', async () => {
    const tracker = document.querySelector('#receipt-tracker').textContent.trim();
    try {await navigator.clipboard.writeText(tracker);copy.textContent='Tracker copied ✓';}
    catch {copy.textContent='Select and copy the tracker above';}
  });
  const download = document.querySelector('[data-download-tracker]');
  if(download) download.addEventListener('click', () => {
    const tracker=document.querySelector('#receipt-tracker').textContent.trim();
    const election=document.querySelector('[data-election-name]').textContent.trim();
    const blob=new Blob([`Verifiable Vote — synthetic demo receipt\nElection: ${election}\nBallot tracker: ${tracker}\n\nCheck this tracker against the published ballot list. Revoting may supersede this ballot.\n`],{type:'text/plain'});
    const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='ballot-receipt.txt';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
})();
