create table public.pending_transactions (
  merchant_transaction_id text not null,
  user_id uuid not null,
  created_at timestamp with time zone null default now(),
  amount integer null,
  constraint pending_transactions_pkey primary key (merchant_transaction_id),
  constraint pending_transactions_user_id_fkey foreign KEY (user_id) references auth.users (id) on delete CASCADE
) TABLESPACE pg_default;