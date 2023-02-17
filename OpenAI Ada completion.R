library(pacman)

pacchetti_da_usare <- c("tidyverse", "googledrive", "Rtsne", 
                        "quanteda", "openai", "jsonlite", "haven", "httr2")
pacman::p_load(char = pacchetti_da_usare)

wd <- setwd("C:/Users/Vahin/Desktop")

df <- haven::read_sav(paste(wd, "Letta_electionday_campione.sav", sep = "/"))

df_text <- df["text"]
df_text$category <- NULL

Sys.setenv(
  OPENAI_API_KEY = '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'
)


for (j in 1:nrow(df_text)) {
  res <- tryCatch(
    {
      create_completion(
        model = "ada:ft-personal-2023-02-15-13-29-31",
        prompt = paste0(substring(df_text$text[j], 1, 97), "\n\n###\n\n"),
        temperature = 0,
        top_p = 1,
        max_tokens = 3,
        echo = FALSE)
    },
    error=function(cond) {
      return(NULL)
    })

  if (!is.null(res)) {

    df_text$category[j] <- trimws(res$choices$text)

  } else {
    # try one more time

    res <- tryCatch(
      {
        create_completion(
          model = "ada:ft-personal-2023-02-15-13-29-31",
          prompt = paste0(substring(df_text$text[j], 1, 97), "\n\n###\n\n"),
          temperature = 0,
          top_p = 1,
          max_tokens = 3,
          echo = FALSE)
      },
      error=function(cond) {
        return(NA)
      })

    if (!is.null(res)) {
      df_text$category[j] <- trimws(res$choices$text)
    } else {
      df_text$category[j] <- "API failed!"
    }
  }

  res <- NULL

  Sys.sleep(1)
}

df_text <- df_text %>% 
  rename(self_classification = category)
df_text$self_classification <- gsub("#", "", df_text$self_classification)
df_text$self_classification <- sub(" .*", "", df_text$self_classification)
df_text$self_classification <- str_replace(df_text$self_classification, "civilement", "civile")

df <- cbind(df, df_text$self_classification)
df <- df %>% rename(self_classification = "df_text$self_classification")
df <- df %>% relocate(self_classification, .before = source)

write_sav(df, "C:/Users/Vahin/Desktop/Letta - campione con autoclassificazione.sav")
