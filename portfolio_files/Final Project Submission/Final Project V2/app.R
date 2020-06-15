library(shiny)
library(ggplot2)
library(plotly)
library(viridis)
library(scales)

ui <- navbarPage(
  title = "Midterms '18", #BRIAN UI SECTION 
  tabPanel("Interactive Map", 
           titlePanel("Interactive Map"),
           sidebarLayout(
             sidebarPanel(radioButtons(
               inputId="mapChoice", label="Heat map options", choices = c("Eligible Voter Turnout","Rural-Urban Concentration","Percentage Black Voters","Margins per voting percentage"),
               selected="Eligible Voter Turnout"),
               titlePanel("Top 5 Counties in PA"),
               tableOutput(outputId="PAtable"),
               titlePanel("Top 5 Counties in OH"),
               tableOutput(outputId="OHtable")
             ),
             mainPanel(
               plotOutput(outputId = "paPlot"),
               plotOutput(outputId = "ohPlot"))
           )
  ), 
  #NIKKI UI SECTION
  tabPanel("Demographic Correlations",
           titlePanel("Race and Voter tendencies in 2018 Midterm Election"),
           sidebarLayout(
             sidebarPanel(
               selectInput("statename","Select a State", c("Ohio", "Pennsylvania" ))
             ),
             
             mainPanel(
               plotOutput("one")
             ))), 
  tabPanel("Urban-Rural Characteristics",
           sidebarLayout(
             sidebarPanel(
               selectInput("State","Select a State", c("OH", "PA" )),
               sliderInput("bins",
                           "Number of bins:",
                           min = 1,
                           max = 20,
                           value = 5)
             ),
             
             mainPanel(
               plotOutput("idk")
             )
           ))
)

server <- function(input, output) {
  
  counties <- map_data("county")
  ohcounty <- subset(counties, region == "ohio")
  pacounty <- subset(counties, region == "pennsylvania")
  ohcounty <- mutate(ohcounty,county=subregion)
  pacounty <- mutate(pacounty,county=subregion)
  
  source("PAmerge.R")
  PA <- getPA() #FINAL PA DATA SET 
  source("OHmerge.R")
  OH <- getOH() #FINAL OH DATA SET 
  
  PA$turnout <- (PA$Dgov18+PA$Rgov18)/PA$cvap
  OH$turnout <- (OH$Dgov18+OH$Rgov18)/OH$cvap
  PA$margin <- abs(PA$Dcongress18-PA$Rcongress18)/PA$cvap
  OH$margin <- abs(OH$Dcongress18-OH$Rcongress18)/OH$cvap
  
  PAmap <- inner_join(PA,pacounty,by="county")
  OHmap <- inner_join(OH,ohcounty, by="county") 
  
  
  #BRIAN SERVER SECTION 
  #BRIAN GRAPHS 
  output$paPlot <- renderPlot({
    plotPicker(input$mapChoice,PAmap)
  })
  
  output$ohPlot <- renderPlot({
    plotPicker(input$mapChoice,OHmap)
  })
  
  output$PAtable <- renderTable({
    topFinder(input$mapChoice,PA)
  })
  
  output$OHtable <- renderTable({
    topFinder(input$mapChoice,OH)
  })
  
  
  #NIKKI SERVER SECTION 
  output$one <- renderPlot({
    if(input$statename=="Ohio"){
      
      ggplot(OH, aes(x=OH$black_pct, y=OH$Dcongress18/OH$cvap))+ geom_point(size=2, shape=19, color= "black")+
        geom_smooth()+ coord_cartesian(ylim=c(0,100))+coord_cartesian(xlim=c(1.2,27))+ 
        scale_y_continuous(labels= percent)+ scale_x_continuous(name= "Proportion of Black Population in each County",
                                                                breaks=seq(0,30,5))+scale_y_continuous(name= "OH Democratic Voter Percentage")
      #NIKKI GRAPHS FOR OH 
    }
    else if(input$statename=="Pennsylvania"){
      
      ggplot(PA, aes(x=PA$black_pct, y=PA$Dcongress18/PA$cvap))+ geom_point(size=2, shape=19, 
                                                                            color= "black")+geom_smooth()+ coord_cartesian(ylim=c(0,100))+coord_cartesian(xlim=c(1.2,27))+ 
        scale_y_continuous(labels= percent)+ scale_x_continuous(name= "Proportion of Black Population in each County", 
                                                                breaks=seq(0,30,5))+scale_y_continuous(name= "PA Democratic Voter Percentage")
      
      #NIKKI GRAPHS FOR PA 
    }
  })
  
  #ALISA SERVER SECTION 
  output$idk <- renderPlot({
    if(input$State=="OH"){
      x <-OH[,39]
      bins <- seq(min(x), max(x), length.out = input$bins + 1)
      hist(OH$ruralurban_cc,breaks=bins,col='darkblue',border='white',
           main="Ruralness of Ohio Counties",xlab = "OH counties", ylab ="1: urban, 10:rural")
      
    }
    else if(input$State=="PA"){
      x <-PA[,39]
      bins <- seq(min(x), max(x), length.out = input$bins + 1)
      hist(PA$ruralurban_cc,breaks=bins,col='darkblue',border='white',
           main = "Ruralness of Pennsylvania Counties",xlab = "PA counties", ylab ="1: urban, 10:rural")
      
    }
  }) 
  
}

#ADDITIONAL FUNCTIONS
plotPicker <- function(choice,dataIn){
  
  gradient <- NULL
  graphOut <- NULL 
  breaks <- NULL
  if(choice=="Eligible Voter Turnout"){
    gradient <- "black_pct"
    breaks <- c(10, 20, 30, 40, 50, 60)
  }else if(choice == "Rural-Urban Concentration"){
    gradient <- "ruralurban_cc"
    breaks <- c(1, 2, 3, 4, 5, 6,7,8,9)
    
  }else if(choice == "Percentage Black Voters"){
    gradient <- "turnout"
    breaks <- c(.1, .2, .3, .4, .5, .6,.7,.8,.9)
  }else if(choice == "Margins per voting percentage"){
    gradient <- "margin"
    breaks <- seq(from = 0, to = 1000, by = 10)
  }
  
  graphOut <- ggplot(data=dataIn) + ggtitle(deparse(substitute(dataIn)))+
    geom_polygon(aes(x=long,y=lat,group=group), fill='white', color='black')+
    coord_fixed(1.3) + 
    geom_polygon(aes(x=long,y=lat,group=group,fill=eval(parse(text=gradient))), color='black') +
    scale_fill_viridis(breaks)+
    theme(legend.position="right")
  
  
  return(graphOut)
}

topFinder <- function(choice, data){
  
  indicator <- NULL
  topn <- 5
  if(choice=="Eligible Voter Turnout"){
    indicator <- "turnout"
  }else if(choice == "Rural-Urban Concentration"){
    indicator <- "ruralurban_cc"
  }else if(choice == "Percentage Black Voters"){
    indicator <- "black_pct"
  }else if(choice == "Margins per voting percentage"){
    indicator <- "margin"
    topn <- -5
  }
  top <- top_n(select(data,county,indicator),n=topn)
  top <- top[order(eval(parse(text=paste("top$",indicator,sep=""))), decreasing = TRUE),]
  top <- top[1:5,]
  return(top)
}

#RUN APP 
shinyApp(ui = ui, server = server)
