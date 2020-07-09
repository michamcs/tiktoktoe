CREATE TABLE `TikTokPost` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `user_id` varchar(255),
  `number_of_likes` int,
  `number_of_share` int,
  `post_text` varchar(255),
  `url` varchar(255)
);

CREATE TABLE `PostHashtags` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `post_id` varchar(255),
  `hashtag_id` varchar(255)
);

CREATE TABLE `UserBioHashtags` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `hashtag_id` varchar(255),
  `user_id` varchar(255)
);

CREATE TABLE `AllHashtags` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `hashtag` varchar(255)
);

CREATE TABLE `Songs` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `post_id` int,
  `song_id` int
);

CREATE TABLE `AllSongs` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `song_name` varchar(255)
);

CREATE TABLE `TikTokUsers` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `user_id` varchar(255),
  `number_of_followers` int,
  `number_of_following` int,
  `number_of_profile_likes` int,
  `bio_text` varchar(255)
);

ALTER TABLE `PostHashtags` ADD FOREIGN KEY (`post_id`) REFERENCES `TikTokPost` (`id`);

ALTER TABLE `AllHashtags` ADD FOREIGN KEY (`id`) REFERENCES `PostHashtags` (`hashtag_id`);

ALTER TABLE `AllHashtags` ADD FOREIGN KEY (`id`) REFERENCES `UserBioHashtags` (`hashtag_id`);

ALTER TABLE `UserBioHashtags` ADD FOREIGN KEY (`user_id`) REFERENCES `TikTokUsers` (`id`);

ALTER TABLE `TikTokPost` ADD FOREIGN KEY (`id`) REFERENCES `Songs` (`post_id`);

ALTER TABLE `Songs` ADD FOREIGN KEY (`song_id`) REFERENCES `AllSongs` (`id`);

ALTER TABLE `TikTokPost` ADD FOREIGN KEY (`user_id`) REFERENCES `TikTokUsers` (`id`);
