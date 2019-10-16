---
layout: post
title: "Our API Style Guide"
subtitle: "Going from comprehensive to minimalistic (and packing a bigger punch)"
category: dev
tags: [api, open-source]
author: Holger Reinhardt
header-img: "images/home-bg.jpg"
---

When I started as CTO at [Haufe Group](https://github.com/Haufe-Lexware) I brought with me over ten years of API experience, starting from the initial enterprise integration around SOA and SOAP all the way to the API economy. So it should not be a surprise that the [Haufe API Style Guide](https://github.com/Haufe-Lexware/api-style-guide) was one of the first visible outcomes of my new role. It still amazes me that we pulled so much information together so quickly and provided such a comprehensive guide on what we - at Haufe - believed our API's should aspire to.

But as the volume of editorial material grew I started to notice something worrisome. In my conversations engineering knew about our guide, and maybe read the intro, but I could not shake the feeling that no one really read it. Maybe flipped through it, but not read it. And only a few very visible guidelines were applied, but a lot of the deeper knowledge and guidance was - kind of - ignored. I did notice that wherever and whenever I provided an API design workshop, the understanding of the non-functional design requirements (Developer Experience, Outside-In) increased, but that was hardly a scalable model.  

Coming to [Adello](https://github.com/adello) I was faced with a similar challenge. We were about to embark on building a SaaS in a Microservices Architecture and the surface (the outward visible design) of the service APIs  would need to be governed by some kind of common style. This time instead of going comprehensive (and honestly: simply cloning the Haufe Styleguide) I went the opposite direction and boiled it down to the very essence of what I consider a good API design. I tried to limit myself to the very critical and core aspects of API design. And yes, that includes such apparently trivial stipulation as no CamelCase'ing (Hint: To scratch the surface of that one read [Why letter casing is important](https://uxplanet.org/why-letter-casing-is-important-to-consider-during-design-decisions-50402acd0a4e) from an UX perspective - I believe that APIs should explicitly NOT follow any programming lingo but embrace plain human English to increase the semantic distance from implementation), but also a repeated emphasize on [Postel's Law or Robustness Principle](https://en.wikipedia.org/wiki/Robustness_principle) as the fundamental law of API design. So we boiled down the API style guide to a single page with bullet points.

In my experience this condensed format works much better with engineering since it is much easier to refer to. And it is more actionable Sure, a lot of the more sophisticated knowledge is lost, but I have come to the conclusion that if we get the basic design right from the start, there is always time to add magic dust as we scale. But if the basics get buried under too much information, it is hard to reap the benefits from an API-driven business or service architecture.

In the spirit of our [Open Source Policy](https://github.com/adello/open-source/blob/master/open-source.md) we would like to share our [API Style Guide](https://github.com/adello/api-style-guide/blob/master/api-style-guide.md) and hope that others can learn from our experiences as we did from theirs.

--

Some very valuable feedback from my dear colleague and friend [@mamund](https://twitter.com/mamund):

Small point, i'd like to see your guideline doc use (outline) numbering, not bullets. makes it a bit easier to refer to when speaking about the guidelines. also, would love to see each of these guidelines having an anchor tag to make it easier to refer to them in docs, emails, and other written comms.

Even smaller point, would love to see more clearly which elements are REQUIRED. there are some references like that in the beginning (Rules) but i think some of the Best Practices ("Service URI should ...") sound like requirements, too.

Love the brevity. When you have this small set, it is easy for others to learn them, remember them, and - therefore - they are more likely to adhere-to/apply them.