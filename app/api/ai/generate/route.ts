import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { prompt, tier } = body;

    if (!prompt) {
      return NextResponse.json({ error: "Prompt is required" }, { status: 400 });
    }

    // ----------------------------------------------------
    // FAKE AI GENERATION (Stubbed for Prototype)
    // ----------------------------------------------------
    await new Promise((resolve) => setTimeout(resolve, 1500));

    const mockResponse = {
      workout_plan: `Mock ${tier || 'Standard'} Workout Plan for: ${prompt}`,
      nutrition_guidelines: "Mock Nutrition: 40% Protein, 30% Carbs, 30% Fats",
      generated_at: new Date().toISOString()
    };

    return NextResponse.json(mockResponse);

  } catch (error) {
    return NextResponse.json({ error: "Failed to generate AI response" }, { status: 500 });
  }
}
