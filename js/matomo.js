var _paq = window._paq || [];
	/* tracker methods like "setCustomDimension" should be called before "trackPageView" */
	_paq.push(["setDocumentTitle", document.domain + "/" + document.title]);
	_paq.push(["setCookieDomain", "*.adello.github.io"]);
	_paq.push(["setDomains", ["*.adello.github.io"]]);
	_paq.push(['trackPageView']);
	_paq.push(['enableLinkTracking']);
	(function() {
	  var u="//www.analytics.corp.adctrl.com/";
	  _paq.push(['setTrackerUrl', u+'matomo.php']);
	  _paq.push(['setSiteId', '4']);
	  var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
	  g.type='text/javascript'; g.async=true; g.defer=true; g.src=u+'matomo.js'; s.parentNode.insertBefore(g,s);
	})();