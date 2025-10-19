create table public.profiles (
  id uuid not null,
  updated_at timestamp with time zone null,
  username text null,
  full_name text null,
  avatar_url text null,
  website text null,
  has_paid boolean null default false,
  constraint profiles_pkey primary key (id),
  constraint profiles_username_key unique (username),
  constraint profiles_id_fkey foreign KEY (id) references auth.users (id) on delete CASCADE
) TABLESPACE pg_default;