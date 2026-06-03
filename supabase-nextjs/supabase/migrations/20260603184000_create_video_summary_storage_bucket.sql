insert into storage.buckets (
  id,
  name,
  public,
  file_size_limit,
  allowed_mime_types
)
values (
  'video-summaries',
  'video-summaries',
  true,
  52428800,
  array[
    'application/json',
    'application/octet-stream',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/x-subrip',
    'audio/mpeg',
    'image/png',
    'text/plain',
    'text/vtt',
    'video/mp4'
  ]
)
on conflict (id) do update
set
  public = excluded.public,
  file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;
