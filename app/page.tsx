"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { optIn } from "@/lib/api";
import type { FitnessGoal } from "@/lib/db";

const GOALS: { value: FitnessGoal; label: string }[] = [
  { value: "cut", label: "Cut — Lose Fat" },
  { value: "bulk", label: "Bulk — Build Muscle" },
  { value: "recomp", label: "Recomp — Both" },
];

export default function OptInPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const form = e.currentTarget;
    const data = new FormData(form);

    try {
      const result = await optIn({
        first_name: data.get("first_name") as string,
        email: data.get("email") as string,
        goal: data.get("goal") as FitnessGoal,
        current_weight_lbs: parseFloat(data.get("current_weight_lbs") as string),
        age: parseInt(data.get("age") as string, 10),
        // UTM params — passed automatically from TikTok/IG/X/LinkedIn links
        utm_source: searchParams.get("utm_source"),
        utm_medium: searchParams.get("utm_medium"),
        utm_campaign: searchParams.get("utm_campaign"),
        referrer: typeof document !== "undefined" ? document.referrer || null : null,
      });

      // Store user_id in a cookie for subsequent page loads
      document.cookie = `user_id=${result.user_id}; path=/; max-age=31536000; SameSite=Lax`;

      router.push("/thank-you-tripwire");
    } catch (err) {
      setError("Something went wrong. Please try again.");
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center p-6 relative overflow-hidden bg-background">
      {/* Background Cyber Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/10 blur-[120px] rounded-full pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-xl w-full relative z-10"
      >
        <div className="text-center mb-8">
          <div className="inline-block px-3 py-1 mb-6 text-xs font-semibold tracking-wider text-primary border border-primary/30 bg-primary/10 rounded-full">
            INITIALIZE METABOLIC OVERRIDE
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-4 text-foreground">
            Unlock <span className="text-primary italic">Free Money</span> in Your Fitness Results
          </h1>
          <p className="text-lg text-muted-foreground">
            Stop guessing. Start optimizing. Download the 15 Science-Backed Tips from Your AI Coach That Pay You Back in Results.
          </p>
        </div>

        <div className="bg-card/50 backdrop-blur-xl border border-border p-8 rounded-2xl shadow-2xl">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="first_name" className="text-foreground/80">First Name</Label>
                <Input
                  id="first_name"
                  name="first_name"
                  placeholder="John"
                  required
                  className="bg-background/50 border-input/50 focus-visible:ring-primary"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="age" className="text-foreground/80">Age</Label>
                <Input
                  id="age"
                  name="age"
                  type="number"
                  placeholder="28"
                  min={18}
                  max={90}
                  required
                  className="bg-background/50 border-input/50 focus-visible:ring-primary"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="email" className="text-foreground/80">Email Address</Label>
              <Input
                id="email"
                name="email"
                type="email"
                placeholder="john@example.com"
                required
                className="bg-background/50 border-input/50 focus-visible:ring-primary"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="goal" className="text-foreground/80">Goal</Label>
                <select
                  id="goal"
                  name="goal"
                  required
                  defaultValue=""
                  className="w-full h-10 rounded-md border border-input/50 bg-background/50 px-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="" disabled>Select...</option>
                  {GOALS.map((g) => (
                    <option key={g.value} value={g.value}>{g.label}</option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="current_weight_lbs" className="text-foreground/80">Weight (lbs)</Label>
                <Input
                  id="current_weight_lbs"
                  name="current_weight_lbs"
                  type="number"
                  placeholder="185"
                  min={71}
                  max={499}
                  step="0.1"
                  required
                  className="bg-background/50 border-input/50 focus-visible:ring-primary"
                />
              </div>
            </div>

            {error && (
              <p className="text-sm text-destructive text-center">{error}</p>
            )}

            <Button
              type="submit"
              disabled={loading}
              className="w-full text-lg h-14 bg-primary hover:bg-primary/90 text-primary-foreground font-bold shadow-[0_0_20px_rgba(var(--primary),0.4)] transition-all hover:shadow-[0_0_30px_rgba(var(--primary),0.6)]"
            >
              {loading ? "INITIALIZING DATA..." : "GET IN THE SYSTEM NOW"}
            </Button>

            <p className="text-center text-xs text-muted-foreground mt-4">
              100% Secure. We will never share your personal data.
            </p>
          </form>
        </div>
      </motion.div>
    </main>
  );
}
