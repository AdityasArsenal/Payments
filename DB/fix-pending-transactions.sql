-- Fix pending_transactions table and RLS policies

-- Create the table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.pending_transactions (
  merchant_transaction_id text NOT NULL,
  user_id uuid NOT NULL,
  created_at timestamp with time zone NULL DEFAULT now(),
  amount integer NULL,
  CONSTRAINT pending_transactions_pkey PRIMARY KEY (merchant_transaction_id),
  CONSTRAINT pending_transactions_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users (id) ON DELETE CASCADE
) TABLESPACE pg_default;

-- Enable RLS
ALTER TABLE public.pending_transactions ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (to avoid conflicts)
DROP POLICY IF EXISTS "Users can read their own pending transactions" ON public.pending_transactions;
DROP POLICY IF EXISTS "Users can insert their own pending transactions" ON public.pending_transactions;

-- Create RLS policies
CREATE POLICY "Users can read their own pending transactions"
  ON public.pending_transactions FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own pending transactions"
  ON public.pending_transactions FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Grant necessary permissions
GRANT ALL ON public.pending_transactions TO authenticated;
GRANT ALL ON public.pending_transactions TO service_role;
