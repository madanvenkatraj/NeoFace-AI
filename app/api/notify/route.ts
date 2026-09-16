import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const { accessToken, toEmail, projectName, projectData } = await req.json();

    if (!accessToken || !toEmail || !projectName) {
      return NextResponse.json(
        { error: 'Missing required fields: accessToken, toEmail, or projectName' },
        { status: 400 }
      );
    }

    // Construct a MIME email message
    const subject = `✅ Render Complete: ${projectName}`;
    const body = `Hello,

Your video render job for the project "${projectName}" has successfully completed.

Project Details:
- Target Resolution: ${projectData?.resolution || '1080p'}
- Frame Rate: ${projectData?.frameRate || '30fps'}
- Compression: ${projectData?.compression || 'High'}

You can now view and download your exported file in NeoFace Studio.

Best,
NeoFace AI Team`;

    const emailLines = [
      `To: ${toEmail}`,
      `Subject: ${subject}`,
      'Content-Type: text/plain; charset=utf-8',
      '',
      body,
    ];
    const emailStr = emailLines.join('\r\n');

    // Base64url encode the string
    const base64EncodedEmail = Buffer.from(emailStr)
      .toString('base64')
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/, '');

    const response = await fetch('https://gmail.googleapis.com/gmail/v1/users/me/messages/send', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        raw: base64EncodedEmail,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Gmail API Error:', errorText);
      return NextResponse.json(
        { error: 'Failed to send email via Gmail API', details: errorText },
        { status: response.status }
      );
    }

    const result = await response.json();
    return NextResponse.json({ success: true, messageId: result.id });
  } catch (error: any) {
    console.error('Internal Error in notify route:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
