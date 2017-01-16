#!/usr/bin/python
#coding=utf-8


class DailyReport():
    """
    writer for daily report
    """
    def __init__(self, report_file, report_title):
        self.report_file = report_file
        self.report_title = report_title
        self.fd = open(report_file, 'w')

    def open(self):
        self.fd.write("<h1 style=\"text-align:center;\"><span style=\"line-height:1.5;\">%s</span></h1>\n" % (self.report_title))


    def write_table_header(self, header_list):
        self.fd.write("<p>\n<table style=\"width:100%;background-color:#CCCCCC;\" cellpadding=\"2\" cellspacing=\"0\" border=\"2\" bordercolor=\"#000000\">\n<tbody>\n")
        
        self.fd.write("<tr>\n")
        for header in header_list:
            self.fd.write("<td style=\"text-align:center;\"><strong><span style=\"font-family:Microsoft YaHei;\">%s</span></strong></td>\n" % (header))
        self.fd.write("</tr>\n")


    def write_table_row(self, row):
        self.fd.write("<tr>\n")
        for cell in row:
            self.fd.write("<td style=\"text-align:center;\">%s</td>\n" % (cell))
        self.fd.write("</tr>\n")


    def write_table_footer(self, footer_list):
        self.fd.write("<tr>\n")
        for footer in footer_list:
            self.fd.write("<td style=\"text-align:center;\">%s</td>\n" % (footer))
        self.fd.write("</tr>\n")

        self.fd.write("</tbody>\n</table>\n</p>\n<hr />\n\n")
        

    def close(self):
        self.fd.close()


class ErrorLogReport():
    """
    writer for error log report
    """
    def __init__(self, report_file):
        self.report_file = report_file
        self.fd = open(report_file, 'w')

    def open(self):
        self.fd.write("<!doctype html>\n<html>\n<meta charset=\"utf-8\"></meta>\n\
                <head>\n<script src=\"http://code.jquery.com/jquery-latest.js\"></script>\n\
                <script>\nfunction mouseDown($this){\n\
                if($this.parentElement.children[1].style.display  === \"none\"){\n\
                    $this.parentElement.children[1].style.top  = $this.parentElement.offsetTop;\n\
                    $this.parentElement.children[1].style.left = $this.parentElement.offsetLeft;\n\
                    $this.parentElement.children[1].style.display='block';\n\
                }\nelse {\n\
                    $this.parentElement.children[1].style.display='none';\n\
                }\n}\n</script>\n\
                <style type=\"text/css\">\n\
                    .style-req-res{\n\
                        display: none;\n\
                        background-color: white;\n\
                        border: 1px solid;\n\
                        position: absolute;\n\
                    }\n\
                </style>\n</head>\n<body>\n"
                )


    def write_table_header(self, header_list):
        self.fd.write("<p>\n<table style=\"width:100%;background-color:#CCCCCC;\" cellpadding=\"2\" cellspacing=\"0\" border=\"2\" bordercolor=\"#000000\">\n<tbody>\n")

        self.fd.write("<tr>\n")
        for header in header_list:
            self.fd.write("<td style=\"text-align:center;\"><strong>%s</strong></td>\n" % (header))
        self.fd.write("</tr>\n\n")


    def write_table_row(self, row):
        self.fd.write("<tr>\n")
        for cell in row[:-2]:
            self.fd.write("<td style=\"text-align:center;\">%s</td>\n" % (cell))
        
        for cell in row[-2:]:
            self.fd.write("<td><label onmousedown=\"mouseDown(this)\"><script type=\"text/html\" style=\"display:block\">%s</script></label><div class=\"style-req-res\"><script type=\"text/html\" style=\"display:block\">%s</script></div></td>\n" % (cell[0:30], cell))

        self.fd.write("</tr>\n\n")


    def write_table_footer(self, footer_list):
        self.fd.write("</tbody>\n</table>\n</p>\n</body>\n</html>\n")


    def close(self):
        self.fd.close()


if __name__ == "__main__":
    pass

