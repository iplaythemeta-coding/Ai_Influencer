"use client";

import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle2, DownloadIcon } from "lucide-react";
import { getUserState, createCheckout } from "@/lib/api";
import type { UserState } from "@/lib/db";

function getUserIdFromCookie(): string | null {
  const match = document.cookie.match(/(?:^|;\s*)user_id=([^;]+)/);
  return match ? match[1] : null;
}

export default function ThankYouTripwirePage() {
  const router = useRouter();
  const [userState, setUserState] = useState<UserState | null>(null);
  const [checkoutLoading, setCheckoutLoading] = useState(false);

  useEffect(() => {
    const userId = getUserIdFromCookie();
    if (!userId) return;
    getUserState(userId).then(setUserState).catch(() => null);
  }, []);

  const alreadyPurchased =
    userState &&
    ["tripwire_active", "pro_active", "ultimate_active"].includes(
      userState.current_funnel_state
    );

  const handleActivate = async () => {
    const userId = getUserIdFromCookie();
    if (!userId) return;
    setCheckoutLoading(true);
    try {
      const { session_url } = await createCheckout(userId, "tripwire");
      window.location.href = session_url;
    } catch {
      setCheckoutLoading(false);
    }
  };

  return (
    <main className="min-h-screen relative p-6 bg-background">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-background pointer-events-none" />

      <div className="max-w-4xl mx-auto space-y-12 relative z-10 py-12">
        {/* Lead Magnet Delivery */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center space-y-4"
        >
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-500/20 text-green-400 mb-4">
            <CheckCircle2 size={32} />
          </div>
          <h1 className="text-3xl md:text-4xl font-bold">You&apos;re In. Protocol Initialized.</h1>
          <p className="text-muted-foreground max-w-xl mx-auto">
            Your &quot;15 Money Magnet Fitness Tips&quot; PDF is on its way to your inbox. You can also download it right now.
          </p>
          <Button variant="outline" className="gap-2 mt-4 hover:bg-primary/10 hover:text-primary">
            <DownloadIcon size={16} />
            Download 15 Tips PDF
          </Button>
        </motion.div>

        {/* If already purchased, show dashboard CTA instead of upsell */}
        {alreadyPurchased ? (
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-center space-y-4"
          >
            <CheckCircle2 className="mx-auto text-primary" size={48} />
            <h2 className="text-2xl font-bold">Blueprint Already Active</h2>
            <p className="text-muted-foreground">You&apos;re already in the system. Head to your dashboard.</p>
            <Button
              onClick={() => router.push("/dashboard")}
              className="h-14 px-10 text-lg font-bold bg-primary hover:bg-primary/90"
            >
              GO TO DASHBOARD
            </Button>
          </motion.div>
        ) : (
          /* Tripwire Pitch */
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="border-primary/30 shadow-[0_0_50px_rgba(var(--primary),0.1)] bg-card/60 backdrop-blur-lg">
              <CardHeader className="text-center border-b border-border/50 bg-primary/5 pb-8">
                <div className="inline-block px-3 py-1 mb-4 text-xs font-bold tracking-widest text-destructive border border-destructive/30 bg-destructive/10 rounded-full">
                  ONE-TIME OFFER
                </div>
                <CardTitle className="text-3xl md:text-5xl font-black text-foreground">
                  Wait! Before you close this tab...
                </CardTitle>
                <CardDescription className="text-lg mt-4 max-w-2xl mx-auto font-medium">
                  The 15 tips will fix your foundation. But if you want to{" "}
                  <span className="text-primary font-bold">shortcut 6 months of trial and error</span>
                  , you need the AI Nutrition Quick-Start Blueprint.
                </CardDescription>
              </CardHeader>
              <CardContent className="grid md:grid-cols-2 gap-8 p-8">
                <div className="space-y-6">
                  <h3 className="text-xl font-bold">What&apos;s inside the Blueprint?</h3>
                  <ul className="space-y-4">
                    {[
                      "AI-Generated Macro Splitting specific to your body type",
                      "7-Day 'Metabolic Reset' Meal Plan",
                      "PulseAI's Top 5 Post-Workout Supplements Database",
                      "Cheat-Day Damage Control Protocols",
                    ].map((feature, i) => (
                      <li key={i} className="flex gap-3 text-muted-foreground">
                        <CheckCircle2 className="text-primary shrink-0" size={20} />
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-background/80 rounded-xl border border-border p-6 flex flex-col justify-center items-center text-center">
                  <p className="text-sm font-bold tracking-widest text-muted-foreground mb-2 line-through">
                    REGULAR PRICE: $97
                  </p>
                  <div className="text-5xl font-black text-primary mb-6">$17</div>
                  <div className="space-y-4 w-full">
                    <Button
                      onClick={handleActivate}
                      disabled={checkoutLoading}
                      className="w-full h-14 text-lg font-bold bg-primary hover:bg-primary/90 text-primary-foreground shadow-[0_0_15px_rgba(var(--primary),0.3)] hover:shadow-[0_0_25px_rgba(var(--primary),0.5)] transition-all"
                    >
                      {checkoutLoading ? "REDIRECTING..." : "ACTIVATE BLUEPRINT"}
                    </Button>
                    <button
                      onClick={() => router.push("/dashboard")}
                      className="text-sm text-muted-foreground hover:text-foreground underline underline-offset-4"
                    >
                      No thanks, I&apos;ll figure my macros out manually.
                    </button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>
    </main>
  );
}
