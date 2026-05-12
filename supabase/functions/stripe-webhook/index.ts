// Stripe Webhook Handler — Supabase Edge Function
// 결제 완료 시 자동으로 벽돌 충전

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import Stripe from "https://esm.sh/stripe@13.0.0?target=deno";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const stripe = new Stripe(Deno.env.get("STRIPE_SECRET_KEY")!, {
  apiVersion: "2023-10-16",
});

const supabase = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
);

const WEBHOOK_SECRET = Deno.env.get("STRIPE_WEBHOOK_SECRET")!;

serve(async (req: Request) => {
  const signature = req.headers.get("stripe-signature");
  if (!signature) {
    return new Response("Missing signature", { status: 400 });
  }

  const body = await req.text();

  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(body, signature, WEBHOOK_SECRET);
  } catch (err) {
    console.error("Webhook signature verification failed:", err);
    return new Response("Invalid signature", { status: 400 });
  }

  // 결제 완료 이벤트만 처리
  if (event.type === "checkout.session.completed") {
    const session = event.data.object as Stripe.Checkout.Session;

    if (session.payment_status === "paid") {
      const userId = session.metadata?.user_id;
      const bricks = parseInt(session.metadata?.bricks || "0");
      const productKey = session.metadata?.product_key || "";

      if (userId && bricks > 0) {
        // 중복 처리 방지: 이미 처리된 세션인지 확인
        const { data: existing } = await supabase
          .from("brick_transactions")
          .select("id")
          .eq("stripe_session_id", session.id)
          .single();

        if (existing) {
          console.log(`Session ${session.id} already processed, skipping`);
          return new Response("Already processed", { status: 200 });
        }

        // 벽돌 충전
        const { data: user } = await supabase
          .from("users")
          .select("bricks")
          .eq("id", userId)
          .single();

        if (user) {
          const newBalance = user.bricks + bricks;

          // 잔액 업데이트
          await supabase
            .from("users")
            .update({ bricks: newBalance })
            .eq("id", userId);

          // 트랜잭션 기록
          await supabase.from("brick_transactions").insert({
            user_id: userId,
            amount: bricks,
            reason: `purchase_${productKey}`,
            stripe_session_id: session.id,
          });

          console.log(
            `✅ ${bricks} bricks added to user ${userId}. New balance: ${newBalance}`
          );
        }
      }
    }
  }

  return new Response(JSON.stringify({ received: true }), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
});
