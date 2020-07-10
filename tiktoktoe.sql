CREATE TABLE `TikTokUsers` (
  `id` int PRIMARY KEY,
  `user_id` varchar(255),
  `number_of_followers` int,
  `number_of_following` int,
  `number_of_profile_likes` int,
  `bio_text` varchar(255)
);

CREATE TABLE `TikTokPost` (
  `id` int PRIMARY KEY,
  `user_id` varchar(255),
  `number_of_likes` int,
  `number_of_share` int,
  `post_text` varchar(255),
  `url` varchar(255),
  FOREIGN KEY (user_id) REFERENCES TikTokUsers(id)
);

CREATE TABLE `AllHashtags` (
  `id` int PRIMARY KEY,
  `hashtag` varchar(255)
);

CREATE TABLE `PostHashtags` (
  `id` int PRIMARY KEY,
  `post_id` varchar(255),
  `hashtag_id` varchar(255),
  FOREIGN KEY (post_id) REFERENCES TikTokPost(id),
  FOREIGN KEY (hashtag_id) REFERENCES AllHashtags(id)
);

CREATE TABLE `UserBioHashtags` (
  `id` int PRIMARY KEY,
  `user_id` varchar(255),
  `hashtag_id` varchar(255),
  FOREIGN KEY (user_id) REFERENCES TikTokUsers(id),
  FOREIGN KEY (hashtag_id) REFERENCES AllHashtags(id)
);

CREATE TABLE `AllSongs` (
  `id` int PRIMARY KEY,
  `song_name` varchar(255)
);

CREATE TABLE `Songs` (
  `id` int PRIMARY KEY,
  `post_id` int,
  `song_id` int,
  FOREIGN KEY (post_id) REFERENCES TikTokPosts(id),
  FOREIGN KEY (song_id) REFERENCES AllSongs(id)
);
