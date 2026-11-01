# Caption mode

Saved user instruction, 23 October 2026. Apply to image captions and caption requests; preserve current media, approved copy and the voice anchor. These writing defaults do not grant publishing or account access.

## Routing and delivery

1. Follow the current explicit platform/subset, language, length, number of alternatives and revision scope first. Recognize Insta/IG, FB, Twitter/X, LinkedIn, Pinterest and WhatsApp. Do not interpret an incidental letter x as a platform instruction.
2. With no override, singular `caption do`, `ek caption`, or `give me a caption` means one Instagram caption only. Default to Hinglish. Bare plural `captions do` or `give me captions` means one version per platform in this order: X, LinkedIn, Pinterest, Instagram, Facebook, WhatsApp. Pinterest's title and description together are one version.
3. An explicit alternatives request stays on its selected platform; if none is selected, use Instagram. Thus `2 captions do` means two Instagram options, `Instagram ke 3 captions do` means three Instagram options, and `captions do sirf LinkedIn aur X ke` means just those two platforms. `In captions ko short karo` revises the existing set; it is not a fresh six-platform command.
   An explicit per-image/per-slide caption request instead maps one distinct labeled caption to each requested final image in order. It is a text-delivery instruction, not evidence that Instagram offers a native multiple-caption UI/API or that the account has access. Native feature support remains unverified without relevant current evidence; do not require it to draft the requested text.
4. Return copy directly. Use platform labels for the pack and Title/Description labels for Pinterest. For a single caption omit the platform lecture, variants, media brief and posting slot. Do not add word counts unless asked. Hashtags belong at the end only where useful, not in a mandatory block.
5. Inspect an available image and use supplied notes. If the image is inaccessible, use only the actual description; do not invent location, clothes, travel, mood, production history or results. If neither media nor usable context exists, request the missing image/topic once. Pinterest/WhatsApp account handles are unnecessary for drafting and must not be invented.

## Platform writing defaults

These target ranges are editorial starting points, not proven optimal lengths or new hard constraints. Shorter is welcome when the image carries the idea. Expand only for actual useful context or an explicit request. Do not pad a simple portrait into a business lesson.

| Platform | Usual image-caption length | Native format and tone | Hashtag default |
|---|---|---|---|
| X | About 80–220 weighted characters; within standard 280 budget | One sharp observation or clear point, at most a short second line. English-led unless asked otherwise. No automatic thread or Premium assumption. | Usually 0–1 relevant tag; existing editorial cap 2 |
| LinkedIn | About 40–90 words for an image; 80–180 only with real process/insight | Specific opening, then 1–3 short paragraphs adding an honest perspective. English-led; no invented career takeaway. A real question is optional. | 0–3 specific tags; existing cap 3 |
| Pinterest | Searchable title about 40–70 characters; description about 200–400 characters | Title plus natural description of the visible subject, style and use/inspiration. Put useful subject words early. English for discovery unless user/audience calls for another language. | Normally none; natural search phrases, no keyword pile |
| Instagram | About 8–35 words for a mood/portrait; 40–100 for genuine context/BTS | Strong first line, short readable continuation if needed, optional relevant CTA. Hinglish by default. Do not re-narrate everything visible. | 0–5 relevant tags, often 2–5 when helpful; existing cap 5 |
| Facebook | About 20–70 words; shorter for a pure portrait | Warm Hinglish, relatable observation or brief supported story; optional genuine question. Keep caption and image connected. | 0–3; no need to fill the existing cap 3 |
| WhatsApp | About 5–20 words, usually 1–2 short lines | Personal Hinglish image/status share caption. Sound like a person speaking to contacts. Use Channels, broadcast or business-message formatting only when requested. | None by default |

Limits and checks:

- Preserve the imported four-platform editorial caps in `brain/platform_rules.json`. Instagram 2,200, LinkedIn 3,000 and Facebook 63,206 are inherited writing/validator caps, not all freshly verified platform maxima. Never write to a maximum merely because it exists.
- For Pinterest, the current organic Pin-spec page states title maximum 100 characters and description maximum 800. Count title and description separately. Do not confuse the 250-character on-image textbox with the description. Put the message in the title/creative too, since descriptions are not visible in home/search feeds.
- For X count the complete posted text, including spaces, line breaks and hashtags, with the official `twitter-text` parser or current platform composer. URLs and Unicode have special weights. Plain Python `len()` is not an accurate platform count. If the parser is unavailable, use a conservative bound (NFC-normalized code points at two units each for URL-free text) and shorten to fit; do not invent an exact weighted count. URL-bearing text needs the proper parser/composer before a fit claim.
- No WhatsApp character maximum is asserted here; the short range is a writing choice for this image/status use case.

## Hooks, freshness and quality

- Choose a hook from the actual idea: a recognisable visual detail, concise feeling, specific supported observation, honest process insight or useful result. Let a curiosity opening deliver its payoff in the caption/image. Never borrow another person's anecdote, statistic or success as Manik's.
- Keep optimism natural. Match an explicitly dark, reflective, playful or devotional mood instead of forcing cheerfulness. No fake bravado, motivational filler, exaggerated reveal, engagement bait or fabricated metrics.
- Adapt the angle: X gets compression, LinkedIn gets a supported perspective, Pinterest gets searchable context, Instagram gets visual/emotional immediacy, Facebook gets conversation, WhatsApp gets a personal line. Repeating the core idea is fine; six copies with hashtag swaps are not adaptation.
- Treat trendy as fresh, culturally relevant phrasing, not a license to claim popularity. For a current trend, viral example or trend-linked caption, do a focused current lookup and inspect the original post/date/context. Record observable public evidence only. A popular post does not establish why it spread; likes do not guarantee this caption's reach. Without evidence, write strong evergreen copy without calling it a verified trend.
- Default to one strongest version per selected platform. Do not attach a virality guarantee or repeat a disclaimer after every caption. Never claim a tested lift from these defaults. Learn performance only from comparable real posts under the existing approval policy.

## Caption checks and core boundary

Caption-only output is plain native copy, not a fabricated publication log. The existing DraftPost/ContentPlan analytics schemas and metrics adapters cover LinkedIn, Instagram, Facebook and X; Pinterest and WhatsApp caption support does not extend those analytics. For a simple caption do a light editorial pass. Independently evaluate a substantial six-platform pack under the main skill's evaluator rule.

Before delivery verify requested platform/count/language, image/context support, distinct native adaptation, actual full-copy length and applicable tag caps. For every platform inspect all public fields, including Pinterest title/description and any first comment, for confidential terms from `brain/confidential_terms.json`, unsupported claims, placeholders, voice violations and bait. Keep unresolved facts visibly pending; do not call incomplete text ready. Reuse deterministic four-platform validation only where its schema fits, with X weighted counting as an additional check. A structural pass is not proof of quality or audience performance.

## Primary-source research, accessed 23 October 2026

Use these as scoped evidence, not a secret viral formula. The ranges and platform tone above are editorial synthesis. Recheck live constraints when needed, and prefer account-specific guidance/real analytics when available without assuming dashboard access.

| Source | Supported finding and scope |
|---|---|
| [X: How to Post](https://help.x.com/en/using-x/how-to-post) | Standard text budget is 280; longer posts require eligible paid features. Do not default to a long post. |
| [X: Counting Characters](https://docs.x.com/fundamentals/counting-characters) | Weighted Unicode, normalized text, special URL handling and the recommended twitter-text parser. Raw string length is insufficient. |
| [X: Hashtags](https://help.x.com/en/using-x/how-to-use-hashtags) | Relevant tags index topics; two or fewer is a recommendation, not a hard platform prohibition. |
| [LinkedIn: CREATE](https://members.linkedin.com/create-start) and [official writing guidance](https://www.linkedin.com/business/talent/blog/talent-acquisition/how-to-write-engaging-post-in-linkedin-feed) (26 November 2024) | A clear opening, personal expertise/perspective, readable paragraphs and useful conversations are supported. The talent article gives examples, not a universal optimum or evidence for invented stories. |
| [Pinterest: organic Pin specifications](https://help.pinterest.com/en-gb/article/review-pin-specs) | Title 100, description 800; descriptions help relevance but do not show in home/search feeds. This resolves older third-party 500-character guidance for this current source. |
| [Instagram: Best Practices hub](https://about.fb.com/news/2024/10/best-practices-education-hub-creators-instagram/) (1 October 2024) | Guidance is updated and includes account-specific creation, engagement and reach advice. This source establishes no guaranteed viral caption length or newly verified hashtag maximum. Preserve the existing five-tag editorial cap. |
| [Facebook: spammy content guidance](https://about.fb.com/news/2025/04/cracking-down-spammy-content-facebook/) (24 April 2025) | Meta addresses distracting long captions with excessive tags and unrelated captions. This is not a blanket penalty on every useful long caption. |
| [WhatsApp: Status](https://blog.whatsapp.com/new-ways-to-enjoy-whatsapp-status) (7 February 2023) | Status is a personal update surface for contacts, supports photos/text and has audience controls. The short caption range is an editorial choice, not a sourced length limit. |

No live account dashboard, private feed, original viral-post performance experiment or new analytics integration was inspected in this update. An Instagram search-explainer fetch was rate-limited and is not used as verified evidence. No ad-only best-performing caption statistic is generalized to organic posts.

## 1–2 November 2026 user routing overrides

- Pinterest must always be delivered as two clearly separate fields/blocks: **Pinterest Title** and **Pinterest Description**. Never merge them into one paragraph.
- Instagram and Facebook use **one shared caption** when both are requested together. Write it so the same copy works natively on both. Do not create separate Instagram and Facebook captions unless Manik explicitly asks for separate versions.
- Therefore bare `captions do` currently yields: X, LinkedIn, Pinterest Title + Pinterest Description, Instagram/Facebook shared caption, and WhatsApp. Platform-specific factual constraints still apply.

Current official research checked 2 November 2026: Facebook introduced user-controlled natural-language interest tuning for Feed/Reels on 13 October 2026. Treat this as evidence that semantic topic relevance and audience interest remain important, **not** as a viral-caption formula or a reason to stuff keywords. No guaranteed reach rule is inferred.
