import anthropic
import datetime
import json
import sys

def get_issue_number():
    """Calculate issue number based on weeks since launch (Vol. 1 = April 6, 2026)."""
    launch = datetime.date(2026, 4, 6)
    today = datetime.date.today()
    delta = (today - launch).days
    return max(1, delta // 7 + 1)

def get_date_ranges():
    """Calculate the three date ranges for the newsletter."""
    today = datetime.date.today()
    # Find the upcoming Sunday (issue date)
    days_until_sunday = (6 - today.weekday()) % 7
    issue_date = today + datetime.timedelta(days=days_until_sunday)

    # This week and next: issue date through 13 days out
    week_start = issue_date
    week_end = issue_date + datetime.timedelta(days=13)

    # Upcoming: 14 days out through ~5 weeks out
    upcoming_start = issue_date + datetime.timedelta(days=14)
    upcoming_end = issue_date + datetime.timedelta(days=35)

    return {
        "issue_date": issue_date.strftime("%B %-d, %Y"),
        "issue_date_raw": issue_date.isoformat(),
        "week_range": f"{week_start.strftime('%B %-d')} – {week_end.strftime('%B %-d')}",
        "upcoming_range": f"{upcoming_start.strftime('%B %-d')} – {upcoming_end.strftime('%B %-d, %Y')}",
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "upcoming_start": upcoming_start.isoformat(),
        "upcoming_end": upcoming_end.isoformat(),
    }

NEWSLETTER_SYSTEM_PROMPT = """You are the editor of East / West Review, a weekly newsletter covering cultural life in Oakland and San Francisco. Your job is to research real, verified events and produce a complete newsletter issue in HTML format.

NEWSLETTER IDENTITY
- Name: East / West Review
- Audience: One person — a curious, culturally engaged person in their 30s–40s based in the Bay Area who has two young nephews (ages 4 and 6) they spend time with
- Tone: Curatorial, warm, design-forward, and genuinely opinionated. Write like a trusted friend who knows what's worth your time. Never generic, never listy, never tourist-y.
- Coverage: Equal Oakland and SF

CATEGORIES (all integrated by date, no separate sections)
- Music — small/mid venues only (The Independent, The Chapel, Freight & Salvage, The Sound Room, Yoshi's, Great American Music Hall, The New Parish, OMCA Garden Stage). Artists like Olivia Dean, Rosalía, Arooj Aftab — soulful, interesting, world-influenced, intimate rooms only. NOT arena shows.
- Dance & Performance — ODC Theater, Yerba Buena Center for the Arts
- Talks & Ideas — City Arts & Lectures (unmissable only), The Long Now / The Interval, Berkeley Arts & Letters, KQED Forum live, Commonwealth Club (selective), The Graduate Oakland, MPSF Speaker Series at the Paramount. Krista Tippett-register speakers: meaning, psychology, spirituality, the examined life. Think Maya Shankar, Bessel van der Kolk, Esther Perel, Robert Sapolsky.
- Film — New releases only (no rep screenings). A24, Neon, MUBI-tier, strong documentaries, notable foreign language films. Also flag: Wild & Scenic Film Festival, SF DocFest, Banff Mountain Film Festival World Tour when they're coming up.
- Books — Author talks at City Arts, Omnivore Books, Clio's Books (exceptional only — 1–2/month max)
- Food & Drink — Event-driven ONLY. Specific pop-ups, winemaker nights, special dinners, new menu launches. NOT standing "go here" recommendations. Spots to watch: Urelio's Pizza pop-ups, Broc Cellars events, Hammerling Wines First Fridays, Biondivino, The Salty Pearl special nights, Oakland Yard events, Ordinaire events, Somebody's Sister events, Goodhot.
- Market — Inner Sunset Flea, Temescal Farmers Market, Grand Lake Farmers Market, Renegade Craft, Head West
- Outdoors & Nature — Golden Gate Audubon, Bay Nature Institute, Friends of Sausal Creek, Tilden Regional Park, Cal Academy events. In-the-know walks and events most people wouldn't find.
- Bring the Boys — Things genuinely fun for a 4 and 6 year old that are also interesting for an adult. Children's Fairyland, Chabot Space & Science Center, Tilden Little Farm, Cal Academy Family Days. NOT boring for adults.

EDITORIAL RULES
1. Every event must be real and verifiable. Use web search to confirm dates, venues, and links.
2. No filler. If a day has nothing worth featuring, skip it. Multiple events on one day only if both genuinely earn it.
3. Talks bar: would a curious person rearrange their week for this? "It's at City Arts" is not enough on its own.
4. Literary events: max 2 per issue, only truly exceptional speakers.
5. Food & drink: only if there's a specific event — a pop-up date, a winemaker night, a special menu. Never "this place is good."
6. Free events get a green "free" badge.
7. Every event needs a real URL link.
8. Tone: no bullet points, no listy writing. Full sentences. Confident editorial voice. Each writeup 3–5 sentences.

STRUCTURE
1. This week and next (date range provided) — day-by-day, events sorted by date
2. Upcoming (date range provided) — date-block layout, events 2–5 weeks out
3. On now — museum exhibitions currently running: OMCA, SFMOMA, de Young, Legion of Honor only

MUSEUMS
Always check and include current exhibitions for:
- OMCA (Oakland) — museumca.org
- SFMOMA (SF) — sfmoma.org
- de Young (SF) — famsf.org
- Legion of Honor (SF) — famsf.org
Note free admission days where relevant.

OUTPUT FORMAT
Return ONLY valid HTML. No markdown, no explanation, no preamble. The HTML should be a complete newsletter using the exact design system below — Cormorant Garamond + Inconsolata typefaces, the specific CSS classes, the exact structure. Start with <div class="n"> and end with </div>.

Use this CSS (include it in a <style> tag at the very top):

<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400;1,600&family=Inconsolata:wght@300;400;500&display=swap');
.n { font-family: 'Cormorant Garamond', serif; max-width: 700px; margin: 0 auto; padding: 2.5rem 1.5rem 4rem; color: #1a1a1a; }
.masthead { margin-bottom: 2.5rem; }
.masthead-name { font-family: 'Cormorant Garamond', serif; font-size: 52px; font-weight: 300; letter-spacing: -1px; line-height: 1; margin: 0 0 0.2rem; }
.masthead-name em { font-style: italic; }
.masthead-rule { height: 1px; background: #1a1a1a; margin: 0.75rem 0 0.6rem; }
.masthead-sub { display: flex; justify-content: space-between; align-items: baseline; }
.masthead-tag { font-family: 'Inconsolata', monospace; font-size: 12px; color: #888; letter-spacing: 0.04em; }
.section-label { font-family: 'Inconsolata', monospace; font-size: 12px; letter-spacing: 0.18em; text-transform: uppercase; color: #aaa; margin-bottom: 2rem; }
.day-block { margin-bottom: 2.25rem; }
.day-header { display: flex; align-items: baseline; gap: 0.75rem; margin-bottom: 1.25rem; }
.day-name { font-family: 'Cormorant Garamond', serif; font-size: 30px; font-weight: 300; font-style: italic; line-height: 1; }
.day-date { font-family: 'Inconsolata', monospace; font-size: 12px; color: #aaa; letter-spacing: 0.04em; padding-top: 2px; }
.day-rule { flex: 1; height: 0.5px; background: #e0e0e0; }
.event { margin-bottom: 1.75rem; padding-left: 1.25rem; border-left: 1.5px solid #e0e0e0; }
.event-meta { display: flex; align-items: center; gap: 8px; margin-bottom: 0.35rem; flex-wrap: wrap; }
.event-cat { font-family: 'Inconsolata', monospace; font-size: 12px; font-weight: 500; letter-spacing: 0.1em; text-transform: uppercase; color: #1a1a1a; }
.event-free { font-family: 'Inconsolata', monospace; font-size: 11px; font-weight: 500; color: #3B6D11; background: #EAF3DE; padding: 1px 7px; border-radius: 2px; }
.event-loc { font-family: 'Inconsolata', monospace; font-size: 12px; color: #aaa; margin-left: auto; text-align: right; }
.oak { color: #854F0B; font-weight: 500; }
.sf  { color: #185FA5; font-weight: 500; }
.event-title { font-family: 'Cormorant Garamond', serif; font-size: 20px; font-weight: 400; line-height: 1.25; margin: 0 0 0.4rem; color: #1a1a1a; }
.event-title em { font-style: italic; }
.event-body { font-family: 'Cormorant Garamond', serif; font-size: 16px; font-weight: 300; line-height: 1.75; color: #555; margin: 0 0 0.5rem; }
.event-body em { font-style: italic; }
.event-link { font-family: 'Inconsolata', monospace; font-size: 11px; color: #aaa; text-decoration: none; border-bottom: 0.5px solid #ccc; padding-bottom: 1px; }
.divider { display: flex; align-items: center; gap: 1rem; margin: 3rem 0 2rem; }
.div-line { flex: 1; height: 0.5px; background: #e0e0e0; }
.div-text { font-family: 'Cormorant Garamond', serif; font-size: 22px; font-weight: 300; font-style: italic; color: #888; white-space: nowrap; }
.future-event { display: grid; grid-template-columns: 60px 1fr; gap: 1.25rem; margin-bottom: 1.75rem; padding-bottom: 1.75rem; border-bottom: 0.5px solid #e0e0e0; }
.future-event:last-child { border-bottom: none; margin-bottom: 0; }
.fdate { text-align: right; padding-top: 3px; }
.fdate-m { font-family: 'Inconsolata', monospace; font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase; color: #aaa; display: block; }
.fdate-d { font-family: 'Cormorant Garamond', serif; font-size: 32px; font-weight: 300; line-height: 1; color: #1a1a1a; display: block; }
.fmeta { display: flex; align-items: center; gap: 8px; margin-bottom: 0.35rem; flex-wrap: wrap; }
.ftitle { font-family: 'Cormorant Garamond', serif; font-size: 19px; font-weight: 400; line-height: 1.25; margin: 0 0 0.35rem; color: #1a1a1a; }
.ftitle em { font-style: italic; }
.fbody { font-family: 'Cormorant Garamond', serif; font-size: 15px; font-weight: 300; line-height: 1.7; color: #555; margin: 0 0 0.5rem; }
.fbody em { font-style: italic; }
.museum { display: grid; grid-template-columns: 120px 1fr; gap: 1.25rem; padding: 1.5rem 0; border-bottom: 0.5px solid #e0e0e0; }
.museum:last-child { border-bottom: none; }
.museum-left { padding-top: 2px; }
.museum-name { font-family: 'Inconsolata', monospace; font-size: 12px; font-weight: 500; letter-spacing: 0.06em; text-transform: uppercase; color: #1a1a1a; display: block; margin-bottom: 4px; }
.museum-city { font-family: 'Inconsolata', monospace; font-size: 12px; color: #aaa; display: block; }
.museum-show { font-family: 'Cormorant Garamond', serif; font-size: 18px; font-weight: 400; line-height: 1.25; margin: 0 0 0.3rem; color: #1a1a1a; }
.museum-show em { font-style: italic; }
.museum-dates { font-family: 'Inconsolata', monospace; font-size: 12px; color: #aaa; margin-bottom: 0.5rem; display: block; }
.museum-body { font-family: 'Cormorant Garamond', serif; font-size: 15px; font-weight: 300; line-height: 1.7; color: #555; margin: 0 0 0.5rem; }
.footer { margin-top: 3rem; padding-top: 1.25rem; border-top: 1px solid #1a1a1a; display: flex; justify-content: space-between; align-items: baseline; }
.footer-name { font-family: 'Cormorant Garamond', serif; font-size: 15px; font-style: italic; font-weight: 300; color: #aaa; }
.footer-info { font-family: 'Inconsolata', monospace; font-size: 12px; color: #aaa; }
</style>
"""

def generate_newsletter(issue_number: int, dates: dict) -> str:
    client = anthropic.Anthropic()

    user_prompt = f"""Generate East / West Review Vol. {issue_number}, issue date {dates['issue_date']}.

Date ranges:
- This week and next: {dates['week_range']}
- Upcoming: {dates['upcoming_range']}

Today's actual date for your web searches: {dates['issue_date_raw']}

Use your web search tool to find real, verified events for each section. Search for:
1. Concerts and music events at The Independent SF, The Chapel SF, Freight & Salvage Berkeley, The New Parish Oakland, Yoshi's Oakland, Great American Music Hall SF, OMCA events
2. Dance and performance at ODC Theater SF, Yerba Buena Center SF
3. Talks at City Arts & Lectures, Long Now/The Interval, MPSF Speaker Series Paramount Oakland, Commonwealth Club, Berkeley Arts & Letters
4. Food & drink pop-ups and special events (Urelio's Pizza, Hammerling Wines First Fridays, Broc Cellars, Biondivino, The Salty Pearl, Oakland Yard, Ordinaire, Somebody's Sister)
5. Outdoor/nature events from Golden Gate Audubon, Bay Nature Institute, Tilden Regional Park, Cal Academy
6. Family/kids events at Children's Fairyland Oakland, Chabot Space & Science Center Oakland
7. Markets: Inner Sunset Flea, Temescal Farmers Market special events
8. New film releases worth flagging (A24, Neon, strong documentaries, foreign language)
9. Current exhibitions at OMCA, SFMOMA, de Young, Legion of Honor

Apply strict editorial judgment:
- Only include events that genuinely earn their place
- Skip days with nothing worth featuring
- Food & drink only if there's a specific event, not a standing recommendation
- Literary/talks: max 2 per issue, only unmissable
- Verify every date and link before including

Return ONLY the complete HTML newsletter. No explanation, no markdown, no preamble. Start with <style> and end with </div>."""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=8000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        system=NEWSLETTER_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}]
    )

    # Extract text content from response (may include tool use blocks)
    html_content = ""
    for block in response.content:
        if block.type == "text":
            html_content += block.text

    if not html_content.strip():
        raise ValueError("No HTML content generated")

    return html_content.strip()

if __name__ == "__main__":
    dates = get_date_ranges()
    issue_number = get_issue_number()

    print(f"Generating East / West Review Vol. {issue_number} ({dates['issue_date']})...")

    html = generate_newsletter(issue_number, dates)

    output_file = f"newsletter_vol{issue_number}.html"
    with open(output_file, "w") as f:
        f.write(html)

    print(f"Generated: {output_file}")
    print(f"Characters: {len(html)}")

    # Output for use by send script
    print(f"OUTPUT_FILE={output_file}")
    print(f"ISSUE_NUMBER={issue_number}")
    print(f"ISSUE_DATE={dates['issue_date']}")
