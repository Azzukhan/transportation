import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Logo } from "@/components/Brand/Logo";
import { toast } from "sonner";
import { Lock } from "lucide-react";

const LoginPage = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(false);

  const redirectParam = new URLSearchParams(location.search).get("redirect");
  const redirectTo = redirectParam ? decodeURIComponent(redirectParam) : "/dashboard";

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    const data = new FormData(e.currentTarget);
    try {
      await login({
        username: data.get("username") as string,
        password: data.get("password") as string,
      });
      navigate(redirectTo, { replace: true });
    } catch {
      toast.error("Login failed. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-4 md:p-6 bg-[radial-gradient(circle_at_20%_20%,hsl(var(--primary)/0.45),transparent_35%),radial-gradient(circle_at_80%_80%,hsl(var(--accent)/0.15),transparent_40%),linear-gradient(135deg,hsl(220_70%_20%),hsl(218_72%_12%))] flex items-center justify-center">
      <motion.div
        initial={{ opacity: 0, y: 26, scale: 0.96 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.45 }}
        className="w-full max-w-md rounded-3xl border border-white/15 bg-white/95 backdrop-blur-md shadow-elevated p-7 md:p-8"
      >
        <div className="text-center mb-7">
          <div className="flex justify-center mb-4">
            <Logo size="lg" subtitle="Admin Workspace" />
          </div>
          <h1 className="font-display text-4xl font-bold leading-tight">Welcome Back</h1>
          <p className="text-muted-foreground mt-1">Sign in to access admin operations</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm font-semibold mb-1.5 block">Username</label>
            <Input
              className="h-12 rounded-xl"
              name="username"
              required
              autoComplete="username"
              placeholder="Enter your username"
            />
          </div>
          <div>
            <label className="text-sm font-semibold mb-1.5 block">Password</label>
            <Input
              className="h-12 rounded-xl"
              name="password"
              type="password"
              required
              autoComplete="current-password"
              placeholder="Enter your password"
            />
          </div>

          <Button
            type="submit"
            disabled={loading}
            className="w-full h-11 bg-accent-gradient text-accent-foreground shadow-accent-glow hover:opacity-95 border-0"
          >
            {loading ? "Signing in..." : "Sign In"} <Lock className="ml-2" size={16} />
          </Button>
        </form>
      </motion.div>
    </div>
  );
};

export default LoginPage;
