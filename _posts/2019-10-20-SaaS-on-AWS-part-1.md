---
layout: post
title: "Building SaaS on AWS Serverless - Part 1"
subtitle: "Programmatic advertising explained"
category: dev
tags: [adtech, cloud]
author: Holger Reinhardt
header-img: "images/home-bg.jpg"
---

On September 26th, 2019 I presented our 5 month journey of building our mobile marketing platform [adello.direct](https://www.adello.direct) on AWS Serverless as part of the [Haufe TEC Day](http://work.haufegroup.io/TEC-Day-2019-rundowni/). 

In this blog post I will  try to demystify programmatic advertisement. If you want to follow along with my notes, please continue reading below the slides.

<iframe src="//www.slideshare.net/slideshow/embed_code/key/19E9wASHT6CQF3" width="595" height="485" frameborder="0" marginwidth="0" marginheight="0" scrolling="no" style="border:1px solid #CCC; border-width:1px; margin-bottom:5px; max-width: 100%;" allowfullscreen> </iframe>

Even though the vast majority of us have been using advertising-financed apps and mobile website on our mobile phones just a few understand the amazing technology powering this huge market. 

Starting from slide 6 you will find the basic components of what constitutes something like a stock exchange but for online advertising. On one side there are apps and websites which include SDK's from one or more ad exchanges like [Google's AdX](https://developers.google.com/ad-manager/mobile-ads-sdk) or [Rubicon](https://rubiconproject.com) or [Smaatoo](https://www.smaato.com) just to name a few. Those seller of advertisement space on their respective app or website are the **supply** side of the market. On the other side you have the buyers of advertising, the advertising agencies or companies wanting to run ads. This is the **demand** side. Since the ad exchanges are programmatic marketplaces, the actual buying of ads is realized through so called [Demand Side Platforms aka DSP's](https://developers.google.com/third-party-ads/adx-vendors). We will see in a minute how. 

As in a stock market, demand and supply are highly variable and prices are set through an auction process. There are various auction types, i.e. first price auction or second price auction but lets leave that for another blog post. What you should take away from this is that the auctions are happening in real-time through a bidding process. This is where the so called Real-Time-Bidder (RTB) comes in. The RTB is the equivalent of a stock broker on the exchange floor deciding which of the millions of available ad spaces at any given second to bid on and at what price. Slide 7 shows the basic flow. To give you a feeling of the kind of real-time I am talking about, consider the numbers on slide 8. The bidding process has to be completed within 100ms and resulting play-out of the winning ad (aka the ad campaign having made the winning bid) has to be completed in 10ms. So we are talking real realtime. In those 100ms you - as DSP - have to not just decide which ad space (i.e. mobile app or mobile website) to bid for but also how much to bid.

We can of course all have different opinions about advertising, but from a technical point of view this is real tech no matter how you dice it and slice it.

Adello decided very early on to deploy machine learning at the real-time bidder - like five years before machine learning became cool and everyone was doing it (at least in Powerpoint presentations ;-)). Depending on the depth of the mobile advertising funnel your ad campaign is targeting (slide 9), machine learning models would make the decision for which ad space to bid and how much. Those machine learning models were trained by the millions of transactions happening daily on those real-time marketplaces. No wonder that the inspiration of the core technology of Adello came from high-frequency trading systems. But while the sheer number of transactions is mind-blowing, slide 10 tells you why machine learning is ultimately a numbers games. In Adello I was first introduced to the rule of 1000 - for each funnel stage you need to have at least a 1000 data points to create a somewhat meaningful ML model. Consider that only a fraction of users ever pass from one funnel stage to the next and one quickly realizes the massive scale of data needed on the top of the funnel by calculating backwards. 

In our experience the numbers hold up all the way to Landings. But beyond optimizing for Landings things get complicated. Not just because of the large number of Impressions this requires, but also because a lot of times there is a break in media. While you might click on an ad for an Opera on the way home in the subway, will you buy the tickets on your mobile or will you take a mental note and buy it from your laptop later in the evening. Lets just say there are ways to correlate, but it is not longer straightforward and involves a deeper integration with the e-commerce system of the customer.

Slide 11 shows our Machine Learning Loop we use to optimize mobile advertising campaigns for our customers. Our [creatives (= mobile ads)](https://www.adello.com/products/creative-gallery/) are designed to engage and are instrumented to measure engagement. These signals feed into the first step of the loop. The data is normalized, cleaned (i.e. location data), enriched (by device and context), and checked for any fraud indicators during the second step. 

The resulting data stream is then feed into the models to identify clusters of indicators predicting a certain performance at the chosen primary KPI (i.e. low cost per impressions for archiving reach) together with a secondary KPI (i.e. a certain floor of the click-rate). Keep  in mind that the KPI's do not necessarily have a linear relationship. A low cost per impressions might make certain volume publishers attractive where the click-rate is below the average. Balancing out those sometimes competing KPI's is where machine learning excels. But truth being told, we deploy heuristics and statistical methods in addition to ML.

One of the most important lessons is on slide 12: **Machine Learning today works in robust markets where you don't have to be right all the time.** 

In the current hype cycle it is easy to forget that there is a difference between Alexa responding 'I did not get that' and a car attempting to drive autonomously on a normal street. With Alexa you get the chance to repeat your question, maybe vary it like a seasoned Google Search user hunting for the right kind of words resulting in the best result. Getting hit by car because the color of your jacket was not part of the training set might mean that you will not get a second chance. So when you read the next time of machine learning this and machine learning that, keep that sobering thought in mind. Not seeing the forest because of the trees might become literal truth in regard to the current state of Machine Learning. Which is why - despite of it all - programmatic advertising might not be a bad place to learn Machine Learning in production.

