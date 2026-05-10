use once_cell::sync::Lazy;
use std::env;
use std::path::PathBuf;

pub static CONFIG: Lazy<Config> = Lazy::new(|| Config::from_env());

pub struct Config {
    pub app_id: i32,
    pub api_hash: String,
    pub bot_token: String,
    pub logs_channel: i64,
    pub mongodb_url: String,
    pub mongodb_dbname: String,
    pub bot_owner: i64,
    pub download_location: PathBuf,
    pub thumb_location: PathBuf,
    pub tg_max_size: u64,
    pub max_message_length: usize,
    pub chunk_size: usize,
    pub bot_thumb: PathBuf,
    pub max_concurrent_tasks: usize,
    pub max_task_duration_extract: u64,
    pub max_task_duration_merge: u64,
}

impl Config {
    fn from_env() -> Self {
        let base = env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
        Self {
            app_id: env::var("APP_ID").expect("APP_ID not set").parse().expect("APP_ID int"),
            api_hash: env::var("API_HASH").expect("API_HASH not set"),
            bot_token: env::var("BOT_TOKEN").expect("BOT_TOKEN not set"),
            logs_channel: env::var("LOGS_CHANNEL").expect("LOGS_CHANNEL not set")
                .trim().parse().expect("LOGS_CHANNEL int"),
            mongodb_url: env::var("MONGODB_URL").expect("MONGODB_URL not set"),
            mongodb_dbname: env::var("MONGODB_DBNAME").unwrap_or("Unzipper_Bot".into()),
            bot_owner: env::var("BOT_OWNER").expect("BOT_OWNER not set")
                .parse().expect("BOT_OWNER int"),
            download_location: base.join("Downloaded"),
            thumb_location: base.join("Thumbnails"),
            tg_max_size: 2_097_152_000,
            max_message_length: 4096,
            chunk_size: 512 * 1024,
            bot_thumb: base.join("bot_thumb.jpg"),
            max_concurrent_tasks: 75,
            max_task_duration_extract: 120 * 60,
            max_task_duration_merge: 240 * 60,
        }
    }
}
