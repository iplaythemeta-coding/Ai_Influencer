"use server";

import { revalidatePath } from "next/cache";

export async function submitOptIn(formData: FormData) {
  const name = formData.get("name") as string;
  const email = formData.get("email") as string;

  if (!name || !email) {
    return { error: "Name and email are required." };
  }

  // ----------------------------------------------------
  // FAKE DATABASE INSERTION (Stubbed for Prototype)
  // ----------------------------------------------------
  // In a real app, this would be:
  // const user = await supabase.from('users').insert({ name, email }).select().single();
  // ----------------------------------------------------
  
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 800));

  console.log(`[DB MOCK] Opt-In Processed: ${name} (${email})`);

  // Return a mock user ID and success state
  return { 
    success: true, 
    userId: `usr_mock_${Math.random().toString(36).substring(2, 9)}`,
    redirectUrl: "/thank-you-tripwire"
  };
}
