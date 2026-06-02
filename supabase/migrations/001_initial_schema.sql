-- IdeaOps v1 — Initial Schema

create extension if not exists "pgcrypto";

-- 1. idea_submissions
create table idea_submissions (
    id             uuid primary key default gen_random_uuid(),
    created_at     timestamptz not null default now(),
    source         text not null check (source in ('web', 'sms')),
    user_phone     text,
    raw_text       text not null,
    status         text not null default 'pending' check (status in ('pending', 'processing', 'completed', 'failed', 'partial_success')),
    latest_run_id  uuid
);

-- 2. workflow_runs
create table workflow_runs (
    id                uuid primary key default gen_random_uuid(),
    idea_id           uuid not null references idea_submissions(id) on delete cascade,
    created_at        timestamptz not null default now(),
    status            text not null default 'running' check (status in ('running', 'completed', 'failed', 'partial_success')),
    classifier_output jsonb,
    scoring_output    jsonb,
    planning_output   jsonb,
    task_output       jsonb,
    notion_page_id    text,
    notion_url        text,
    error_message     text
);

-- add FK from idea_submissions.latest_run_id → workflow_runs.id
alter table idea_submissions
    add constraint fk_latest_run
    foreign key (latest_run_id) references workflow_runs(id);

-- 3. generated_tasks
create table generated_tasks (
    id              uuid primary key default gen_random_uuid(),
    run_id          uuid not null references workflow_runs(id) on delete cascade,
    title           text not null,
    description     text not null,
    priority        text not null check (priority in ('high', 'medium', 'low')),
    order_index     int not null,
    estimated_hours numeric not null
);

-- 4. agent_step_logs (observability)
create table agent_step_logs (
    id            uuid primary key default gen_random_uuid(),
    run_id        uuid not null references workflow_runs(id) on delete cascade,
    step_name     text not null,
    status        text not null check (status in ('started', 'completed', 'failed')),
    input_json    jsonb,
    output_json   jsonb,
    error_message text,
    created_at    timestamptz not null default now()
);

-- Indexes
create index idx_workflow_runs_idea_id on workflow_runs(idea_id);
create index idx_generated_tasks_run_id on generated_tasks(run_id);
create index idx_agent_step_logs_run_id on agent_step_logs(run_id);
create index idx_idea_submissions_status on idea_submissions(status);
