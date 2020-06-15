library(readr)
library(dplyr) #DPLYR CHEAT SHEET: https://www.rstudio.com/wp-content/uploads/2015/02/data-wrangling-cheatsheet.pdf 
library(stringr)
getOH <- function() {
  #LOADING DATA
  past_elections <- data.frame(read_csv("past_elections.csv"))
  Ohio_cleaned <- data.frame(read_csv("Ohio_cleaned.csv",
                                      col_names = FALSE))
  #CLEANING AND SUBSETTING DATA
  past_elections <- mutate_all(past_elections, tolower)
  OHelections <- subset(past_elections, past_elections$state == 'ohio')
  Ohio_cleaned <- subset(Ohio_cleaned, !is.na(Ohio_cleaned[,1]))
  
  #FUNCTION TO ADD VOTES TO OVERLAPPING RACES
  sum_cols <- function(Ohio_cleaned,i,col) {
    new_votes <- suppressWarnings(as.numeric(gsub(",","",Ohio_cleaned[,i])))
    if(col %in% names(Ohio_cleaned)){
      Ohio_cleaned[,col] <- Ohio_cleaned[,col]+new_votes
    }else{
      Ohio_cleaned[,col] <-new_votes
    }
    return(Ohio_cleaned)
  }
  
  #MERGE OVERLAPPING RACES AND RENAME 
  last_pos <- NA
  cols <- seq(1,6)
  for(i in seq(7,309)){
    if(!is.na(Ohio_cleaned[1,i])){
      last_pos <- Ohio_cleaned[1,i]
    }
    party <- gsub("[(-)]","",str_extract(Ohio_cleaned[2,i],"[(].[)]"))
    if(is.na(party)){next}
    col <- NA
    if(str_detect(last_pos,"Governor")){
      col <- paste(party,"gov18",sep="")
    }else if(str_detect(last_pos,"State Senator")){
      col <- paste(party,"statesen18",sep="")
    }else if(str_detect(last_pos,"State Representative")){
      col <- paste(party,"staterep18",sep="")
    }else if(str_detect(last_pos,"U.S. Senator")){
      col <- paste(party,"ussen18",sep="")
    }else if(str_detect(last_pos,"Congress")){
      col <- paste(party,"congress18",sep="")
    }else{next}
    Ohio_cleaned <- sum_cols(Ohio_cleaned,i,col)
  }
  
  #FINISH CLEANING
  Ohio_cleaned <- Ohio_cleaned[,-2:-309]
  Ohio_cleaned <- Ohio_cleaned[-1:-4,]
  names(Ohio_cleaned)[1] <- "county"
  Ohio_cleaned$county <- tolower(Ohio_cleaned$county)
  
  mergedOH_elections <- inner_join(OHelections,Ohio_cleaned,by=c("county" = "county"))
  mergedOH_elections[,3:length(mergedOH_elections)] <- sapply(mergedOH_elections[,3:length(mergedOH_elections)], as.numeric)
  return(mergedOH_elections)
}





