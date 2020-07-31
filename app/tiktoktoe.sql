CREATE TABLE TikTokUsers (
  user_id INT PRIMARY KEY AUTO_INCREMENT,
  user_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  number_of_followers BIGINT,
  number_of_following BIGINT,
  number_of_likes BIGINT,
  bio_text VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
);

CREATE TABLE TikTokPost (
  post_id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  number_of_likes BIGINT,
  number_of_share BIGINT,
  number_of_comments BIGINT,
  post_text VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  url VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  FOREIGN KEY (user_id) REFERENCES TikTokUsers(user_id)
);

CREATE TABLE AllHashtags (
  hash_id INT PRIMARY KEY AUTO_INCREMENT,
  hashtag VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
);

CREATE TABLE PostHashtags (
  id INT PRIMARY KEY AUTO_INCREMENT,
  post_id INT,
  hash_id INT,
  FOREIGN KEY (post_id) REFERENCES TikTokPost(post_id),
  FOREIGN KEY (hash_id) REFERENCES AllHashtags(hash_id)
);

CREATE TABLE UserBioHashtags (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  hash_id INT,
  FOREIGN KEY (user_id) REFERENCES TikTokUsers(user_id),
  FOREIGN KEY (hash_id) REFERENCES AllHashtags(hash_id)
);

CREATE TABLE AllSongs (
  song_id INT PRIMARY KEY AUTO_INCREMENT,
  song_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
);

CREATE TABLE Songs (
  id INT PRIMARY KEY AUTO_INCREMENT,
  post_id INT,
  song_id INT,
  FOREIGN KEY (post_id) REFERENCES TikTokPost(post_id),
  FOREIGN KEY (song_id) REFERENCES AllSongs(song_id)
);

CREATE TABLE Tweets (
    tweet_id INT PRIMARY KEY AUTO_INCREMENT,
    hash_id INT,
    twitter_user VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    text VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    url VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    FOREIGN KEY (hash_id) REFERENCES AllHashtags(hash_id)
);