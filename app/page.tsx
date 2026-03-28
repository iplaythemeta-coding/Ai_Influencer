"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import { submitOptIn } from "@/app/actions/optin";

export default function OptInPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    
    // Convert form elements to FormData object for the server action
    const formData = new FormData(e.currentTarget);
    
    // Call the server action
    const result = await submitOptIn(formData);
    
    if (result.success && result.redirectUrl) {
      router.push(result.redirectUrl);
    } else {
      setLoading(false);
      console.error(result.error);
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
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="name" className="text-foreground/80">First Name</Label>
              <Input 
                id="name" 
                placeholder="John" 
                required 
                className="bg-background/50 border-input/50 focus-visible:ring-primary"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email" className="text-foreground/80">Email Address</Label>
              <Input 
                id="email" 
                type="email" 
                placeholder="john@example.com" 
                required 
                className="bg-background/50 border-input/50 focus-visible:ring-primary"
              />
            </div>

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
