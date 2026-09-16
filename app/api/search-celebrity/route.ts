import { GoogleGenAI } from "@google/genai";
import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
    const { query } = await req.json();

    if (!query) {
      return NextResponse.json({ error: "Query is required" }, { status: 400 });
    }

    const prompt = `Search for high-quality, clear portrait photos of the celebrity or person: "${query}". 
Return a JSON array of objects, where each object has a "url" property containing a direct link to a high-quality image of their face, and a "title" property.
Make sure the URLs are direct image links (e.g., ending in .jpg or .png) if possible.
Only return the raw JSON array. Example: [{"url": "https://example.com/face.jpg", "title": "John Doe Portrait"}]`;

    const response = await ai.models.generateContent({
      model: "gemini-3.5-flash",
      contents: prompt,
      config: {
        tools: [{ googleSearch: {} }],
        responseMimeType: "application/json",
        temperature: 0.2
      }
    });

    const text = response.text || "[]";
    const cleanedText = text.replace(/```json\n/g, '').replace(/```/g, '').trim();
    const data = JSON.parse(cleanedText);
    return NextResponse.json({ results: data });
  } catch (error: any) {
    console.error("Search error:", error);
    return NextResponse.json({ error: error.message || "Failed to search" }, { status: 500 });
  }
}
