---
layout: post
title: Rich Media Mobile Creatives
subtitle: Seamless publisher integration
category: frontend
tags: [frontend, mobile]
author: Cătălin Berța
header-img: "images/Rich-Media-Mobile-Creatives/header-bg.jpg"
---

As an introductory article to the frontend section of the blog, we would like to give a quick overview of some of the best practices that our creatives go through before being delivered to various publishers. Those publishers come in many forms and sizes.

The speed of the publisher web pages can be often hurt by 3rd party content. The publishers have no control over what the content loads on its end, how big the files are or how that impacts the end-user experience.

Here at Adello, we do not only care how our creatives impact the publisher's overall page performance. We are also very aware that what helps the publisher, helps us. Two main points would be load speed and seamless integration.
So to ensure that our creatives load seamlessly in their environment, here are a few rules of thumb we follow that are mainly categorized into two aspects, best practices and improvements.

### Vanilla Code
It is tempting to jump over using online libraries to get things done quicker and easier, such as jQuery, Bootstrap, GreenSock to name a few. However, if they are not heavily used, such as in a full-featured website, they add too much overhead and impact load and browsing performance.<br>
Taking [jQuery](https://jquery.com/) as example, nowadays, JavaScript is better supported in most browsers and we no longer have to cover so much cross-browser compatibility solutions. Already, a wide number of jQuery methods are supported natively by JavaScript and I don't need to say this, but native is better, and faster!
Here are just a few common examples where JavaScript shines over methods that were popularly used with jQuery:

```javascript
$('.myClassName');     /* vs */  document.querySelector('.myClassName');
$(parent).append(el);  /* vs */  parent.appendChild(el);
$(el).clone();         /* vs */  el.cloneNode(true);
$(el).outerHeight();   /* vs */  el.offsetHeight
$(el).offset();        /* vs */  el.getBoundingClientRect();
$.proxy(fn, context);  /* vs */  fn.bind(context);
```

When using a popular library, there is also the concern of version conflict with the one on the publisher. 
I will stress a bit that jQuery and other similar libraries and frameworks still have strong uses, however, creatives are lighter in their nature and we need to weigh the use versus overhead.

### Naming Convention and Code Structure
Our creatives get loaded in various environments, in friendly or non-friendly iframes, inside native apps, but a significant amount of times, a creative is also loaded directly in the publisher's topframe. This means our styling and javascript has direct access to the publisher's DOM, and vice versa.
A good start is having a consistent and safer naming convention. We start all of our classes and ids with a prefix, making them less likely to be targeted by the publisher styles. 
Though when styling our creatives, we have to be careful not to create global selectors that can target the publisher's elements as well, so we tie all of our styles to a main namespace, as illustrated below:

```css
/* BAD */
.myCreativeUUID { margin: 0; }
.header { min-height: 50px; }
.hide { display: none; }
``` 

```css
/* GOOD */
.myCreativeUUID { margin: 0; }
.myCreative .header { min-height: 50px; }
.myCreative .header.hide { display: none; }
``` 

This process gets much easier by using a css pre-processor, such as Less or Sass.

In JavaScript we have a similar situation, where sometimes methods and functionality is added directly onto the global namespace. This can cause collision with the publisher's variables or methods.
To avoid that, we use a pattern to add the entire creative functionality under one single exposed prefixed variable.

### No Frameworks or Boilerplates
Another easy reach for simplicity is a CSS boilerplate to either normalize or stylize html elements so that we no longer have to write basic styles. Though, since a creative is very light in its nature when it comes to its mark-up language, even a simple boilerplate can be overhead. This leads to having normalization of elements you don't use or having to rewrite the normalization styles anyway.
We did, however, create a custom css reset style that only takes care of some basic resetting, because for our purposes,  we only need to target a few elements that are more creative focused.


```less
// Less reset
html {
	min-height:100%;
	min-width:100%;
}

body {
	min-height:100%;
	min-width:100%;
	margin:0;
}

#myCreativeUUID {
	-webkit-tap-highlight-color:rgba(0,0,0,0);
	
	& * {
		-webkit-tap-highlight-color:rgba(0,0,0,0);
	}
	
	-webkit-font-smoothing:antialiased;
	-ms-touch-action:none;
	-ms-user-select:none;
	-webkit-touch-callout:none;
	-webkit-user-select:none;
	
	&::selection {
		background-color:transparent;
	}
	&::-moz-selection {
		background-color:transparent;
	}
	
	& a {
		outline:none;
	}
	& a img {
		outline:none;
	}
	& img {
		border:0;
	}
}
```

Another popular reset css I can recommend is from [John Meyer](https://meyerweb.com/eric/tools/css/reset/), mainly for being lightweight due to only taking care of basic resetting.

### Code minification
Code minification goes without saying, the final code that gets delivered no longer needs to be human readable. Therefore, we can apply code minification to remove comments, spaces, new lines and other unnecessary code for the machine. Most importantly, this can also be applied for css and html, where unnecessary code can be removed. 

Sources are also bundled into a single file to reduce the clutter of HTTP requests in the browser.

In general, the entire minification process can reduce up to 60% and that is a significant change in the creative's load time.

### Loading resources async over sync
Scripts should be loaded async, otherwise they block rendering and increase the publisher page's overall loading time. If we need to write javascript that depends on a script, the solution is to simply use the onload callback to run JavaScript after the dependency was loaded. This will allow the script to be parsed in parallel with other resources.

Snippet to inline load a script async with callback function:

```javascript
var head = document.getElementsByTagName('head')[0];
var script = document.createElement('script');
script.src = "path/to/script";
script.onload = scriptLoaded;
head.appendChild(script);

function scriptLoaded() {
  // Script loaded
}
```

So far, we have looked at a few basic best practices, but we go the extra mile, as there are some improvements we can perform that would make the integration even smoother.

### Avoiding Scroll Jank with Passive Event listeners 
Ever swiped a page to scroll but it simply lagged or stuttered? That is usually Scroll Jank and it is caused by event listeners in the page. Instead of scrolling smoothly, the browser has to check each event listener, such as touchstart or touchmove, to make sure that it is not trying to block the scrolling by calling the `event.preventDefault` method, losing precious time and performance doing so. The problem comes when there are such event listeners that don't block scrolling, but the browser has to check them anyway. And here is where Passive Event listeners come in. They are able to promise the browser that you will not call `event.preventDefault()` and the browser no longer has to check and can continue the scroll smoothly.

Adding a passive event listener:
```javascript
element.addEventListener('touchstart', function() {}, {passive: true});
```


While they have been here for quite a while, they are used in the 3rd parameter for an event listener. This means that for older browser which do not support them, the above will translate into an event listener with Capture Event enabled, since the object `{passive: true}` will be read as a truthy value. But in order to ensure you can use it safely in older browsers, a detection for Passive Events Listeners can be used before attaching them:

```javascript
var supportsPassive = false;
try {
var opts = Object.defineProperty({}, 'passive', {
	get: function() {
		supportsPassive = true;
	}
});
window.addEventListener("testPassive", null, opts);
window.removeEventListener("testPassive", null, opts);
}catch(e){}
```

Now being able to use it like so:

```javascript
element.addEventListener('touchstart', function() {}, supportsPassive ? {passive: true} : false);
```

The Passive Event listeners were mainly created for mobile and it is a game changer for 3rd party content as well. This is why we use them, to ensure that we do not impact the scrolling performance for the publishers that run our creatives.

### Optimized assets and sprites 
Assets are usually the heaviest in size when delivering 3rd party content and need the extra attention. There are mainly two methods to approach image optimization, through spritesheets and compression.  
#### SpriteSheet
A spritesheet is the combination of multiple images into a single larger one. This leads to less memory used and better performance by having less requests.
#### Compression
For lighter assets that don't require an alpha channel, we use JPG with a standard compression rate of 80% for optimal image quality / file size ratio. As well, we strip all the metadata and use Progressive Encoding instead of the default "Baseline mode", for faster display.
Though, there are more modern image formats, such as WebP and JP2 (JPG 2000), that have a superior compression and better quality characteristics than their counterparts, JPG and PNG.
The support for JP2 has not grown as predicted, but it is supported by Safari, where as WebP is more popular, but not yet supported by Safari. With that in mind, we can use some simple methods to detect which is supported and use them accordingly.
Detection methods for WebP and JP2 support:

```javascript
function testWebP(callback) {
	var webP = newImage();
	webP.onload = webP.onerror = function() {
	callback(webP.height == 2);
};
//2x2WebPimage
webP.src = 'data:image/webp;base64,UklGRjoAAABXRUJQVlA4IC4AAACyAgCdASoCAAIALmk0mk0iIiIiIgBoSygABc6WWgAA/veff/0PP8bA//LwYAAA';
}

//TestJP2Support
function testJPEG2000(callback) {
	var JP2 = newImage();
	JP2.onload = JP2.onerror = function() {
	callback(JP2.height == 2);
};
//2x2JPEG2000image
JP2.src='data:image/jp2;base64,/0//UQAyAAAAAAABAAAAAgAAAAAAAAAAAAAABAAAAAQAAAAAAAAAAAAEBwEBBwEBBwEBBwEB/1IADAAAAAEAAAQEAAH/XAAEQED/ZAAlAAFDcmVhdGVkIGJ5IE9wZW5KUEVHIHZlcnNpb24gMi4wLjD/kAAKAAAAAABYAAH/UwAJAQAABAQAAf9dAAUBQED/UwAJAgAABAQAAf9dAAUCQED/UwAJAwAABAQAAf9dAAUDQED/k8+kEAGvz6QQAa/PpBABr994EAk//9k=';
}
```

While there is a substantial number of ways to optimize and improve web content, here we touched some that are more focused on 3rd Party Development.

In the end, the grand goal is to deliver lightweight creatives that seamlessly load and integrate in the publisher's page.