create table image_embedded (
    id serial primary key,
    context text,
    embedding vector(512)
);