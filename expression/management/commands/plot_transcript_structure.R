suppressMessages(library("ggplot2"))
suppressMessages(library("dplyr"))
suppressMessages(library("ggtranscript"))
suppressMessages(library("base64enc"))

# first argument = gtf
args <- commandArgs(trailingOnly = TRUE)
gtfPath <- args[1]
#gtfPath <- 'C:/Users/sl693/Dropbox/Scripts/isoVisDev/expression/df.csv'
message("Loading gtf for plotting")
print(gtfPath)

plot_simply <- function(gtfPath){

  gtf <- read.table(gtfPath, sep = ",", header = T)
  gexons <- gtf %>% dplyr::filter(feature == "exon")

  #gexons_rescaled <- shorten_gaps(
  #gexons, 
  #to_intron(gexons, "isoform"), 
  #group_var = "isoform"
  #)

  p <- gexons %>%
    ggplot(aes(
        xstart = start,
        xend = end,
        y = isoform
    )) +
    geom_range() +
    geom_intron(
        data = to_intron(gexons, "isoform"),
        aes(strand = strand)
    ) +
    theme_classic() +
    labs(y = NULL) +
    theme(axis.line=element_blank(),axis.text.x=element_blank(),
          axis.text.y=element_blank(),axis.ticks=element_blank(),
          axis.title.x=element_blank(),
          axis.title.y=element_blank(),legend.position="none",
          panel.background=element_blank(),panel.border=element_blank(),panel.grid.major=element_blank(),
          panel.grid.minor=element_blank(),plot.background=element_blank())

  return(p)
}

p <- plot_simply(gtfPath)

png("C:/Users/skl215/Dropbox/Scripts/isoVisDev/expression/static/plots/transcript_plot.png")
print(p)
dev.off()