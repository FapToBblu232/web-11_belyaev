```dbml
// Use DBML to define your database structure
// Docs: https://dbml.dbdiagram.io/docs
Table User {
  id integer [pk]
  email varchar
  password varchar

  created_at timestamp
  updated_at timestamp
}

Table UserProfile {
  id integer [pk]
  avatar varchar
  nickname varchar
  user_id integer [ref: - User.id]
}

Table Question {
  id integer [pk]
  title varchar
  content text
  author_id integer [ref: > User.id]
  is_active boolean

  tag_id integer

  created_at timestamp
  updated_at timestamp

  likes_count integer
  dislikes_count integer
}

Table Answer {
  id integer [pk]
  question_id integer [ref: > Question.id]
  content text
  author_id integer [ref: > User.id]
  parent_answer_id integer [ref: - Answer.id]
  is_active boolean

  created_at timestamp
  updated_at timestamp

  likes_count integer
  dislikes_count integer
}

Table QuestionReactions {
  id integer [pk]
  author_id integer [ref: > User.id]
  question_id integer [ref: > Question.id]
  is_like boolean

  indexes {
    (author_id, question_id) [unique]
  }
}

Table AnswerReactions {
  id integer [pk]
  author_id integer [ref: > User.id]
  answer_id integer [ref: > Answer.id]
  is_like boolean
  indexes {
    (author_id, answer_id) [unique]
  }
}

Table Tag {
  id integer [ref: <> Question.tag_id]
  name varchar
}
```
