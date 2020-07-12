CREATE TABLE `TikTokUsers` (
  `user_id` INTEGER PRIMARY KEY,
  `user_name` varchar(255),
  `number_of_followers` int,
  `number_of_following` int,
  `number_of_likes` int,
  `bio_text` varchar(255)
);

CREATE TABLE `TikTokPost` (
  `post_id` INTEGER PRIMARY KEY,
  `user_id` int,
  `number_of_likes` int,
  `number_of_share` int,
  `number_of_comments` int,
  `post_text` varchar(255),
  `url` varchar(255),
  FOREIGN KEY (user_id) REFERENCES TikTokUsers(user_id)
);

CREATE TABLE `AllHashtags` (
  `hash_id` INTEGER PRIMARY KEY,
  `hashtag` varchar(255)
);

CREATE TABLE `PostHashtags` (
  `id` INTEGER PRIMARY KEY,
  `post_id` varchar(255),
  `hash_id` varchar(255),
  FOREIGN KEY (post_id) REFERENCES TikTokPost(post_id),
  FOREIGN KEY (hash_id) REFERENCES AllHashtags(hash_id)
);

CREATE TABLE `UserBioHashtags` (
  `id` INTEGER PRIMARY KEY,
  `user_id` varchar(255),
  `hash_id` varchar(255),
  FOREIGN KEY (user_id) REFERENCES TikTokUsers(user_id),
  FOREIGN KEY (hash_id) REFERENCES AllHashtags(hash_id)
);

CREATE TABLE `AllSongs` (
  `song_id` INTEGER PRIMARY KEY,
  `song_name` varchar(255)
);

CREATE TABLE `Songs` (
  `id` INTEGER PRIMARY KEY,
  `post_id` int,
  `song_id` int,
  FOREIGN KEY (post_id) REFERENCES TikTokPost(post_id),
  FOREIGN KEY (song_id) REFERENCES AllSongs(song_id)
);
