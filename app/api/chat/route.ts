import { GoogleGenAI } from "@google/genai";
import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const { messages } = await req.json();
    const apiKey = process.env.GEMINI_API_KEY;
    
    if (!apiKey) {
      return NextResponse.json({ error: "Gemini API Key missing" }, { status: 500 });
    }

    const ai = new GoogleGenAI({ apiKey });
    
    // Format history for the model
    // Assuming messages is an array of { role: 'user' | 'assistant', content: string }
    const history = messages.slice(0, -1).map((msg: any) => ({
      role: msg.role === 'assistant' ? 'model' : 'user',
      parts: [{ text: msg.content }]
    }));
    const lastMessage = messages[messages.length - 1].content;

    const chat = ai.chats.create({
      model: "gemini-3.5-flash",
      config: {
        systemInstruction: "You are the NeoFace AI Studio assistant. You help users with face swapping, exporting, applying masks, and configuring settings. You can guide them through the UI or answer technical questions. Keep your responses concise and helpful.",
        tools: [{ googleSearch: {} }],
      }
    });

    // We can't set history easily on `create` without passing it into sendMessage if we want to retain state in a stateless HTTP API. 
    // Wait, the new SDK lets you pass history to chats.create
    const chatWithHistory = ai.chats.create({
      model: "gemini-3.5-flash",
      config: {
        systemInstruction: "You are the NeoFace AI Studio assistant. You help users with face swapping, exporting, applying masks, and configuring settings. You can guide them through the UI or answer technical questions. Keep your responses concise and helpful.",
        tools: [{ googleSearch: {} }],
      },
      history: history
    });

    const response = await chatWithHistory.sendMessage({ message: lastMessage });
    
    return NextResponse.json({ text: response.text });
  } catch (error: any) {
    console.error("Chat error:", error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
