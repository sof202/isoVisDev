library("ggplot2")
library("dplyr")
library("ggtranscript")

# first argument = gtf
#args <- commandArgs(trailingOnly = TRUE)
gtfPath <- 'C:/Users/sl693/Dropbox/Scripts/isoVisDev/expression/df.csv'

print("RRRRRRRRRRRRR")
plot_simply <- function(gtfPath){

  print(gtfPath)

  gtf = read.table(gtfPath, sep = ",", header = T)
  print("read")
  gexons = gtf
  print(colnames(gexons))
  gexons <- gtf %>% dplyr::filter(feature == "exon")

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
    )

  return(p)
}

p <- plot_simply(gtfPath)

png("C:/Users/sl693/Dropbox/Scripts/isoVisDev/expression/static/plots/transcript_plot.png")
print(p)
dev.off()