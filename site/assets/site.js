(function () {
  'use strict';

  const GA_ID = 'G-19VR75D8BG';
  const CONSENT_KEY = 'pettraffic_analytics_consent';

  // Saugus naršyklės saugyklos naudojimas
  function getConsent() {
    try {
      return localStorage.getItem(CONSENT_KEY);
    } catch (error) {
      return null;
    }
  }

  function saveConsent(value) {
    try {
      localStorage.setItem(CONSENT_KEY, value);
      return true;
    } catch (error) {
      return false;
    }
  }

  // Mobilusis meniu
  const menuButton = document.querySelector('#menu');
  const nav = document.querySelector('#nav');

  if (menuButton && nav) {
    menuButton.addEventListener('click', () => {
      const isOpen = nav.classList.toggle('open');
      menuButton.setAttribute('aria-expanded', String(isOpen));
    });

    nav.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        nav.classList.remove('open');
        menuButton.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // Straipsnių paieška ir teminiai filtrai pagrindiniame puslapyje
  const articleSearch = document.querySelector('#article-search');
  const articleCards = Array.from(document.querySelectorAll('#article-grid .article-card'));
  const filterButtons = Array.from(document.querySelectorAll('[data-filter]'));
  const noResults = document.querySelector('#no-results');
  const resultsStatus = document.querySelector('#article-results-status');
  let activeFilter = 'visi';

  function filterArticles() {
    if (!articleCards.length) return;
    const query = articleSearch ? articleSearch.value.trim().toLocaleLowerCase('lt-LT') : '';
    let visibleCount = 0;

    articleCards.forEach((card) => {
      const categories = (card.dataset.category || '').split(/\s+/);
      const matchesCategory = activeFilter === 'visi' || categories.includes(activeFilter);
      const matchesText = !query || card.textContent.toLocaleLowerCase('lt-LT').includes(query);
      const visible = matchesCategory && matchesText;
      card.hidden = !visible;
      if (visible) visibleCount += 1;
    });

    if (noResults) noResults.hidden = visibleCount > 0;
    if (resultsStatus) {
      resultsStatus.textContent = 'Rodoma ' + visibleCount + ' iš ' + articleCards.length + ' straipsnių.';
    }
  }

  filterButtons.forEach((button) => {
    button.addEventListener('click', () => {
      activeFilter = button.dataset.filter || 'visi';
      filterButtons.forEach((item) => {
        const active = item === button;
        item.classList.toggle('active', active);
        item.setAttribute('aria-pressed', String(active));
      });
      filterArticles();
    });
  });

  if (articleSearch) articleSearch.addEventListener('input', filterArticles);

  document.querySelectorAll('[data-topic-link]').forEach((link) => {
    link.addEventListener('click', () => {
      const topic = link.dataset.topicLink;
      const matchingButton = filterButtons.find((button) => button.dataset.filter === topic);
      if (matchingButton) matchingButton.click();
    });
  });

  // Patogus straipsnio ir svetainės dalijimasis
  const shareTarget = document.querySelector('main .article') ||
    document.querySelector('main .closing > div');

  if (shareTarget && navigator) {
    const shareBox = document.createElement('section');
    shareBox.className = 'pt-share';
    shareBox.setAttribute('aria-label', 'Pasidalyti šiuo puslapiu');

    const shareText = document.createElement('p');
    shareText.textContent = 'Manote, kad šis patarimas gali būti naudingas kitam augintinio šeimininkui?';

    const shareButton = document.createElement('button');
    shareButton.type = 'button';
    shareButton.className = 'pt-share-button';
    shareButton.textContent = 'Pasidalyti patarimu';

    const shareStatus = document.createElement('span');
    shareStatus.className = 'pt-share-status';
    shareStatus.setAttribute('role', 'status');
    shareStatus.setAttribute('aria-live', 'polite');

    shareButton.addEventListener('click', async () => {
      const shareData = {
        title: document.title,
        text: 'Praktiškas patarimas šunų ir kačių šeimininkams – Pet traffic',
        url: window.location.href
      };

      try {
        if (typeof navigator.share === 'function') {
          await navigator.share(shareData);
          shareStatus.textContent = 'Ačiū, kad dalijatės!';
        } else if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
          await navigator.clipboard.writeText(shareData.url);
          shareStatus.textContent = 'Nuoroda nukopijuota – galite ją išsiųsti draugui.';
        } else {
          shareStatus.textContent = 'Nukopijuokite puslapio adresą iš naršyklės ir pasidalykite juo.';
        }
      } catch (error) {
        if (error && error.name !== 'AbortError') {
          shareStatus.textContent = 'Nepavyko pasidalyti automatiškai. Nukopijuokite puslapio adresą.';
        }
      }
    });

    shareBox.append(shareText, shareButton, shareStatus);
    if (shareTarget.classList.contains('article')) {
      const articleMeta = shareTarget.querySelector('.article-meta');
      if (articleMeta) articleMeta.insertAdjacentElement('afterend', shareBox);
      else shareTarget.prepend(shareBox);
    } else {
      shareTarget.appendChild(shareBox);
    }
  }

  // Google Analytics paleidžiamas tik gavus sutikimą
  function enableAnalytics() {
    if (window.petTrafficAnalyticsLoaded) return;

    window.petTrafficAnalyticsLoaded = true;
    window.dataLayer = window.dataLayer || [];

    function gtag() {
      window.dataLayer.push(arguments);
    }

    window.gtag = gtag;
    gtag('js', new Date());
    gtag('config', GA_ID);

    const script = document.createElement('script');
    script.async = true;
    script.src =
      'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;

    document.head.appendChild(script);
  }

  // Google Analytics slapukų šalinimas
  function removeAnalyticsCookies() {
    const names = document.cookie
      .split(';')
      .map(cookie => cookie.split('=')[0].trim());

    names.forEach(name => {
      if (
        name === '_ga' ||
        name.startsWith('_ga_') ||
        name === '_gid' ||
        name.startsWith('_gat')
      ) {
        document.cookie =
          name + '=; Max-Age=0; path=/; SameSite=Lax';
      }
    });
  }

  // Sutikimo lango stiliai
  const style = document.createElement('style');

  style.textContent = `
    #pt-cookie-box {
      position: fixed;
      z-index: 99999;
      bottom: 16px;
      left: 16px;
      right: 16px;
      max-width: 620px;
      margin: auto;
      padding: 20px;
      background: #fff;
      color: #222;
      border: 1px solid #ddd;
      border-radius: 14px;
      box-shadow: 0 4px 25px #0003;
      font: 15px/1.5 Arial, sans-serif;
    }

    #pt-cookie-box h2 {
      margin: 0 0 8px;
      font-size: 19px;
    }

    #pt-cookie-box p {
      margin: 0 0 14px;
    }

    #pt-cookie-box button {
      padding: 11px 15px;
      margin: 4px;
      border: 1px solid #777;
      border-radius: 8px;
      background: #fff;
      color: #222;
      font-weight: bold;
      cursor: pointer;
    }

    #pt-cookie-box button:focus-visible {
      outline: 3px solid #2869bd;
      outline-offset: 2px;
    }

    .pt-share {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 10px 14px;
      margin: 22px 0;
      padding: 16px 18px;
      border: 1px solid #e6dfd2;
      border-radius: 14px;
      background: #fbf8f1;
      color: #34352f;
    }

    .pt-share p {
      flex: 1 1 220px;
      margin: 0;
    }

    .pt-share-button {
      padding: 10px 15px;
      border: 0;
      border-radius: 8px;
      background: #354c3b;
      color: #fff;
      font-weight: 700;
      cursor: pointer;
    }

    .pt-share-status {
      flex-basis: 100%;
      font-size: 13px;
    }

    #pt-cookie-settings {
      position: fixed;
      z-index: 99998;
      bottom: 10px;
      left: 10px;
      padding: 9px 12px;
      border: 1px solid #777;
      border-radius: 8px;
      background: #fff;
      color: #222;
      cursor: pointer;
    }
  `;

  document.head.appendChild(style);

  // Nuolatinis nustatymų mygtukas
  const settingsButton = document.createElement('button');

  settingsButton.id = 'pt-cookie-settings';
  settingsButton.textContent = 'Slapukų nustatymai';
  settingsButton.type = 'button';

  document.body.appendChild(settingsButton);

  function showConsent() {
    const oldBox = document.querySelector('#pt-cookie-box');

    if (oldBox) oldBox.remove();

    const box = document.createElement('section');

    box.id = 'pt-cookie-box';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'true');
    box.setAttribute('aria-label', 'Slapukų pasirinkimas');

    const heading = document.createElement('h2');
    heading.textContent = 'Jūsų privatumas svarbus';

    const paragraph = document.createElement('p');

    paragraph.textContent =
      'Jūsų pasirinkimas įsimenamas naršyklėje, kad nereikėtų ' +
      'jo klausti kiekvieno apsilankymo metu. Tik gavę jūsų ' +
      'sutikimą įjungsime Google Analytics lankomumo statistikai rinkti.';

    const accept = document.createElement('button');

    accept.type = 'button';
    accept.textContent = 'Sutinku';

    const reject = document.createElement('button');

    reject.type = 'button';
    reject.textContent = 'Nesutinku';

    accept.addEventListener('click', () => {
      const saved = saveConsent('accepted');

      if (saved) {
        window.location.reload();
      } else {
        enableAnalytics();
        box.remove();
      }
    });

    reject.addEventListener('click', () => {
      saveConsent('rejected');
      removeAnalyticsCookies();
      window.location.reload();
    });

    box.append(heading, paragraph, accept, reject);
    document.body.appendChild(box);

    accept.focus();
  }

  settingsButton.addEventListener('click', showConsent);

  // Ankstesnio pasirinkimo patikrinimas
  const consent = getConsent();

  if (consent === 'accepted') {
    enableAnalytics();
  } else if (consent !== 'rejected') {
    showConsent();
  }
})();
