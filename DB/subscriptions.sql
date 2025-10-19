-- Ensure required extensions
create extension if not exists pgcrypto;

-- Subscriptions table
create table if not exists public.subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  status text not null default 'active',
  start_date timestamptz not null default now(),
  end_date timestamptz not null,
  plan_id text null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Payments table
create table if not exists public.payments (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  subscription_id uuid null references public.subscriptions(id) on delete set null,
  amount integer not null, -- paise
  payment_date timestamptz not null default now(),
  payment_status text not null, -- pending, completed, failed, etc
  transaction_id text not null unique,
  provider text not null default 'PHONEPE',
  raw_response jsonb null
);

-- Basic RLS
alter table public.subscriptions enable row level security;
alter table public.payments enable row level security;

-- Policies: users may manage their own subscriptions/payments
create policy if not exists "Users can read their own subscriptions"
  on public.subscriptions for select
  using (auth.uid() = user_id);

create policy if not exists "Users can insert their own subscriptions"
  on public.subscriptions for insert
  with check (auth.uid() = user_id);

create policy if not exists "Users can update their own subscriptions"
  on public.subscriptions for update
  using (auth.uid() = user_id);

create policy if not exists "Users can read their own payments"
  on public.payments for select
  using (auth.uid() = user_id);

create policy if not exists "Users can insert their own payments"
  on public.payments for insert
  with check (auth.uid() = user_id);

-- Helper function to ensure an active subscription (upsert-like behavior)
create or replace function public.ensure_active_subscription(
  p_user_id uuid,
  p_start_date timestamptz,
  p_end_date timestamptz
) returns void language plpgsql as $$
begin
  -- If an active subscription exists and overlaps, extend end_date if needed
  if exists (
    select 1 from public.subscriptions s
    where s.user_id = p_user_id
      and s.status = 'active'
      and s.end_date >= now()
  ) then
    update public.subscriptions
    set end_date = greatest(end_date, p_end_date), updated_at = now()
    where user_id = p_user_id and status = 'active';
  else
    insert into public.subscriptions (user_id, status, start_date, end_date)
    values (p_user_id, 'active', p_start_date, p_end_date);
  end if;
end;
$$;