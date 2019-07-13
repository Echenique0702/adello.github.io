---
layout: post
title: GDPR and Developer Culture
subtitle: Will you help us to motivate engineers to write about their work?
category: dev
tags: [cto, culture]
author: Holger Reinhardt
header-img: "images/home-bg.jpg"
---

So let's quickly check - did you notice the cookie banner at the bottom of the page? Did you click on it? Thought so .. you did not! 

And this is exactly the problem. Being able to measure the audience of our developer blog was one of the recurring requests from the engineering team. Engineers like numbers - and very few of us are motivated enough to write about our work irrespective of the audience. The reluctance of engineers to step outside of their safety zone and make themselves visible (and thereby vulnerable) is partly due to the prevailing personality of introverts among software developer. Yet most of us are regular readers of technical blogs. And I would lie if not a lot of my own knowledge and ideas are build upon the experiences and ideas of other technical leaders and engineers. And count me in the camp of those who believe that we owe it to our community to give as much as we take.

Being able to measure our audience became an impediment to motivate more engineers to write about their work and challenges. And since Google Analytics was out of the question for me, I setup an instance of [Matomo](https://matomo.org) to provide web analytics of our public pages within our own setup. 

On a side note: You might ask why not Google Analytics? Lets just say 'free is never free - you just pay differently' and I do not like the bargain Google is offering me. I feel our industry has been so hooked on the 'free-of-charge' drug, that we forgot, that the other side needs to pay salaries too. And if I am not willing to ask my customer for money, I need to sell something else (their data?) to someone who is willing to pay for them. 

I digress, but hang in there with me - I am getting to my point. I am fed up with the countless pundits and moralists complaining about online advertising while at the same time being hooked to the 'free' services paid by advertising. And while I laud the intention of GDPR (see above my refusal to use Google Analytics and instead spending my weekend automating a Matomo deployment), in reality the law ties the hands of a honest business while not addressing the core problem on today's Internet .. the cult of the free. 

It is so easy to complain about folks using Amazon for their convenience and their customer focus. Unless you have been recently trying to return something you bought on an impulse in a real store. Or tried to navigate the 'stuck in the 90s' website of (German) retailers. Yet I still do it, because I do not want to see a world ruled only by a few data conglomerates. I accept the inconvenience as price to pay to preserve a world of diversity I deeply care about.

It also means that we need to get off the cheap drug of free and the idea that 'I can have my cake (i.e. privacy protection) and eat it too (and keep using or reading stuff for free)'. Honest work cost money - there are no ifs and but's. If you are not paying, you are not the customer, but the product.

And at Adello we are competing at least partially with Google - yet in spite of us being completely GDPR compliant, and NOT using cookies and being an EU based local alternative with better KPIs, better [Fraud Prevention and Self-Optimizing campaigns](https://www.adello.com/products/our-products/) and some of the [most innovative Adunit's](https://www.adello.com/products/creative-gallery/), many EU businesses and agencies continue to default to one of the two big names in online advertising because 'no one was ever fired for using Big-G or Big-F ...'. In spite of publicly claiming to be deeply concerned about privacy and online fraud.

---

(Update) In subsequent feedback from a dear friend of mine, he challenged me to substantiate my claims that we have better Fraud Prevention than Big-G or drop it. Obviously I am not going to reveal all and every method we use to detect both pre- and post-click fraud, but one of the most obvious signs of fraud is the origin IP address of the mobile. Simply check if the IP address of the mobile is originating in a data center by a lookup in a GeoIP database like the ones [offered by Maxmind](https://www.maxmind.com). Why such a simple check of mapping IP address to origin is apparently not done on the AD exchanges is simply beyond me. And this is merely the most obvious one. And to pre-empt the argument, that the traffic on ad-exchanges is too much to filter for IP origin, let me explain to you that we are doing this filtering on the bidstream's of the 10 or more global exchanges we are connected to within the 250ms window we are allowed for deciding if we want to bid and setting our bid price. (Maybe another blog article explaining the basics of mobile advertising is in order.) If we can do it in real-time, pls don't tell me that the big players can not do it with a hundred times the engineering resources and engineering budget than we have. Why they are not doing it .. well, I let you, dear reader, decide. Fact is that when I ask customers and agency trading desks how they deal with fraud, the answer is always depressingly the same: "Why should we be concerned about fraud, we are using Big G (or Big F), so there is no fraud."

Ok, enough of a detour.

---

But let me get to the point of my rant - for as long as you do not let me count your visit and I understand what topics you are interested in, our dashboard will show a big fat ZERO for the visitor count and there is no way I can motivate more engineers to share their knowledge. 

If we do it by the book - I need your explicit opt-in for me to count you but if you decide not to do so I cannot degrade my service (aka website) even if you refuse. Again - no ifs and but's. I need to ask you for your permission to track your page view and there is nothing I can do if you say no. Even though your IP is anonymized, your data is not shared, it stays in our server and is not shipped across the world. All I care for is which blog articles you read and some indication where you are from. And there is no image tracking tag snug in, no `sendBeacon` anywhere. And yes - we will honor your 'Do not track' setting. There is a Workable cookie from our job recruitment page, but we do need to recruit for open positions, so that is not optional (and it is nothing I control). If you want, you can audit our blog on [our Github side](https://github.com/adello/adello.github.io).

And guess how many readers decide to opt in? I can tell you .. zero, nada, nil. The crooked will continue to rig the game and track you irrespective - the honest are stuck between a hard rock and a stone. Because if I do not know my audience, the motivation to share by my engineering team is just so much lower. And it almost leaves me in a worst place than not providing audience data to my team in the first place. But thanks to GDPR my hands are tied, and knowledge is not being shared. And maybe that would be an ok price to pay if GDPR would also create a real choice if I wanted to exchange my data for a service with advertising or pay for it with money. But I do not see any evidence for that either. It is time for us collectively wake up and acknowledge that nothing is free - and if a service is worth something to us, we should pay for it. Some might choose data, some might choose money .. other's might just decide it is not worth it. But give me that choice. Because there are developers with family and kids and bills to pay on the other side too.

So here is my challenge to you, dear esteemed reader - will you click 'Approve' below so that I can get engineers (Yes, I am looking at you, Platform team ;) to care and share?

Yours sincerely
Holger

PS: Since we are in the business of sharing, the implementation of the cookie banner on a Jekyll page was inspired by [this blog article](https://jekyllcodex.org/without-plugin/cookie-consent/). How to open a link to the opt-out page in a new tab from within Github pages, I found [this Stackoverflow discussion](https://stackoverflow.com/questions/41915571/open-link-in-new-tab-with-github-markdown-using-target-blank) to be helpful.