library(readr)
library(dplyr) #DPLYR CHEAT SHEET: https://www.rstudio.com/wp-content/uploads/2015/02/data-wrangling-cheatsheet.pdf 
library(reshape2)


getPA <- function() {
  #LOADING DATA
  past_elections <- data.frame(read_csv("past_elections.csv"))
  midterms_2018 <- data.frame(read_csv("Pennsylvania.csv"))
  
  #CLEANING DATA
  midterms_2018 <- mutate_all(midterms_2018, tolower)
  past_elections <- mutate_all(past_elections, tolower)
  
  #SUBSETTING STATE DATA
  PAelections <- subset(past_elections, past_elections$state == 'pennsylvania')
  #OHelections <- subset(past_elections, past_elections$state == 'ohio')
  
  #MERGING PA DATA 
  midterms_2018.office_factors <- factor(midterms_2018$Office.Name)
  midterm_offices <- levels(midterms_2018.office_factors)
  
  midterms_2018$Votes <- as.numeric(midterms_2018$Votes)
  
  #COMBINING ALL RACES WITHIN COUNTIES BY SEAT & PARTY USING DCAST
  midterms_2018_cast <- midterms_2018 %>%
    filter(Office.Name %in% c("governor","representative in congress","united states senator","senator in the general assembly","representative in the general assembly")) %>%
    dcast(County.Name ~ Office.Name + Party.Name, value.var = "Votes", fun.aggregate = sum)
  
  cols <- paste(names(midterms_2018_cast[,-1]),"18",sep="")
  names(midterms_2018_cast) <- c("County.Name",cols)

  mergedPA_elections <- inner_join(PAelections,midterms_2018_cast,by=c("county" = "County.Name"))
  mergedPA_elections[,3:length(mergedPA_elections)] <- sapply(mergedPA_elections[,3:length(mergedPA_elections)], as.numeric)
  
  #RENAMING TO MATCH OH
  new_names <- c("Dgov18","Ggov18","Lgov18","Rgov18","Dcongress18","Lcongress18","Rcongress18",
    "Dstaterep18", "DRstaterep18","Gstaterep18", "Istaterep18", "Lstaterep18","NAstaterep18",
    "Rstaterep18","Dstatesen18","Gstatesen18","Lstatesen18","Rstatesen18","Dussen18",
    "Gussen18","Lussen18","Russen18")
  
  for(i in seq(40,length(mergedPA_elections))){
    names(mergedPA_elections)[i] <- new_names[i-39]
  }
  
  #Final PA Data Set
  return(mergedPA_elections)
}
