const HILI_URL = "your hili server URL"
const HILI_PASS = "your hili key"

async function post(data) {
  const req = new Request(HILI_URL)
  req.headers = {
    'Authentication': HILI_PASS,
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  }
  req.method = 'POST'
  req.body = JSON.stringify(data)
  const resp = await req.load()
}

/** Send the clip **/
async function sendClip(clip, note, tags, srcUrl, dtUrl) {
  const data = {
    href: srcUrl,
    title: dtUrl,
    time: +new Date(),
    text: clip,
    note,
    tags
  }
  await post(data)
}


/* Text to clip, should have been put on the clipboard */
const clip = Pasteboard.paste()

/* If reading in DevonTHINK, parse the item URL */
let dtUrl = '';
if (args.plainTexts.length > 0) {
  let t = args.plainTexts[0].match(/x-devonthink-item.*/)
  if (t !== null && t.length === 1) dtUrl = t[0].trim();
}

/* The URL from the browser */
const ogUrl = args.urls[0]

/* Construct menu */
const alert = new Alert()
alert.title = "clip to hili"
const urlMsg = `\n\n${ogUrl}`
const dtUrlMsg = dtUrl !== '' ? `\n\n${dtUrl}` : ''
alert.message = clip + urlMsg + dtUrlMsg
alert.addTextField("note...")
alert.addTextField("tags (comma-separated)...")
alert.addCancelAction("cancel")
alert.addAction("clip")
const idx = await alert.presentAlert()
if (idx === -1) return

const note = alert.textFieldValue(0)
const tags = alert.textFieldValue(1).split(',').map(t => t.trim())

sendClip(clip, note, tags, ogUrl, dtUrl)
