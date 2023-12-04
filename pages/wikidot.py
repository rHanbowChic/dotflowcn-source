#!/usr/bin/env python
# -*- encoding: UTF8 -*-

# Copyright 2012 Philipp Klaus
# Part of https://github.com/vLj2/wikidot-to-markdown
# Improved 2016 by Christopher Mitchell
# https://github.com/KermMartian/wikidot-to-markdown

import re ## The most important module here!
import string ## for string.join()
#import markdown
import uuid			## to generate random UUIDs using uuid.uuid4()
import postprocess	## Custom postprocessing

class WikidotToMarkdown(object):
    def __init__(self):
        # regex for URL found on http://regexlib.com/REDetails.aspx?regex_id=501
        self.url_regex = r"(http|https|ftp)\://([a-zA-Z0-9\.\-]+(\:[a-zA-Z0-9\.&amp;%\$\-]+)*@)*((25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9])\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])|localhost|([a-zA-Z0-9\-]+\.)*[a-zA-Z0-9\-]+\.(com|edu|gov|int|mil|net|org|biz|arpa|info|name|pro|aero|coop|museum|[a-zA-Z]{2}))(\:[0-9]+)*(/($|[a-zA-Z0-9\.\,\?\'\\\+&amp;%\$#\=~_\-]+))*[/]?"

        self.static_replacements = { '[[toc]]': '', # no equivalent for table of contents in Markdown
                                   }
        self.regex_replacements = { r'([^:])//([\s\S ]*?[^:])//': r"\1''\2''", # italics
                                    r'([^:])\*\*([\s\S ]*?)\*\*': r"\1'''\2'''", # bold
                                    r'([^:])\[!--([\s\S ]*?)--\]': r"\1<!--\2-->", # comments
                                    r'([^:])__([\s\S ]*?)__': r"\1'''\2'''", # underlining → bold
                                    #r'([^:]){{([\s\S ]*?)}}': r'\1`\2`', # inline monospaced text
                                  }
        self.regex_split_condition = r"^\+ ([^\n]*)$"

    def convert(self, text):
        text = '\n'+text+'\n'# add embed in newlines (makes regex replaces work better)
        # first we search for [[code]] statements as we don't want any replacement to happen inside those code blocks!
        code_blocks = dict()
        code_blocks_found = re.findall(re.compile(r'(\[\[code( type="([\S]+)")?\]\]([\s\S ]*?)\[\[/code\]\])',re.MULTILINE), text)
        for code_block_found in code_blocks_found:
            tmp_hash = str(uuid.uuid4())
            text = text.replace(code_block_found[0],tmp_hash,1) # replace code block with a hash - to fill it in later
            code_blocks[tmp_hash] = "\n"+string.join([" " + l for l in code_block_found[-1].strip().split("\n") ],"\n")+"\n"
        for search, replacement in self.static_replacements.items():
            text = text.replace(search,replacement,1)
            
        # search for any of the simpler replacements in the dictionary regex_replacements
        for s_reg, r_reg in self.regex_replacements.items():
            text = re.sub(re.compile(s_reg,re.MULTILINE),r_reg,text)
        # TITLES -- replace '+++ X' with '=== X ==='
        for titles in re.finditer(r"^(\++)([^\n]*)$", text, re.MULTILINE):
            header = ("=" * len(titles.group(1)))
            text = text.replace(titles.group(0), header + (titles.group(2) + " ") + header)
        # LISTS(*) -- replace '  *' with '***' and so on         
        for stars in re.finditer(r"^([ \t]+)\*", text, re.MULTILINE):
            text = text[:stars.start(1)] + ("*" * len(stars.group(1))) + text[stars.end(1):]
        # LISTS(#) -- replace '  #' with '###' and so on
        for hashes in re.finditer(r"^([ \t]+)\*", text, re.MULTILINE):
            text = text[:hashes.start(1)] + ("#" * len(hashes.group(1))) + text[hashes.end(1):]
        # INTERNAL LINKS -- replace [[[bink]]] with [[bink]]
        for inlink in re.finditer(r"\[\[\[([\s\S ]*?)\]\]\]", text):
            text = text.replace(inlink.group(0), "[["+inlink.group(1)+"]]")
        # IMAGES
        for image in re.finditer(r"\[\[image([\s\S ]*?)\]\]", text):
            text = text.replace(image.group(0), "[[File:" + image.group(1) + "]]")
        # START TABLE
        for table in re.finditer(r"\[\[table([\s\S ]*?)\]\]", text):
            #text = text.replace(table.group(0), "{|" + table.group(1))
            text = text.replace(table.group(0), "{|")
        # START ROW
        for row in re.finditer(r"\[\[row([\s\S ]*?)\]\]", text):
            #text = text.replace(row.group(0), "|-" + row.group(1))
            text = text.replace(row.group(0), "|-")
        # START CELL
        for cell in re.finditer(r"\[\[cell([\s\S ]*?)\]\]", text):
            #text = text.replace(cell.group(0), "|" + cell.group(1))
            text = text.replace(cell.group(0), "|")
        # ENDS
        for end in re.finditer(r"\[\[/([\s\S ]*?)\]\]", text):
            token = end.group(1)
            if token == "table":
                text = text.replace(end.group(0), "|}")
            elif token == "row":
                # end row tabs are not necessary in mediawiki
                text = text.replace(end.group(0), "")
            elif token == "cell":
                # end cell tabs are not necessary in mediawiki
                text = text.replace(end.group(0), "")

        # now we substitute back our code blocks
        for tmp_hash, code in code_blocks.items():
            text = text.replace(tmp_hash, code, 1)

        # Process color corrections
        startpos = 0
        while -1 != startpos:
            startpos = text.find("##", startpos)
            pipepos = text.find("|", startpos + 2)
            endpos = text.find("##", startpos + 2)
            if startpos != -1 and pipepos != -1 and endpos != -1 and endpos > pipepos:
                color = text[startpos + 2 : pipepos].strip()
                colored = text[pipepos + 1 : endpos].strip()
                text = text[: startpos] + "<span style=\"color:" + color + "\">" + colored + \
                       "</span>" + text[endpos + 2 :]
                startpos = endpos
                
        # Process math corrections
        startpos = 0
        while -1 != startpos:
            startpos = text.find("[[$", startpos)
            endpos = text.find("$]]", startpos)
            if startpos != -1 and endpos != -1:
                mathtext = text[startpos + 3 : endpos].strip()
                text = text[: startpos] + "<math>" + mathtext + "</math>" + text[endpos + 3 :]
                startpos = endpos

        # Process table corrections
        startpos = 0
        while -1 != startpos:
            startpos = text.find("\n||", startpos)
            if startpos == -1:
                break

            # Find end of table
            endpos = text.find("\n", startpos + 3)
            while endpos < len(text) - 3 and "||" == text[endpos + 1: endpos + 3]:
                endpos = text.find("\n", endpos + 3)

            # Found bounds of text chunk: reformat table
            fixup = text[startpos + 1 : endpos].replace("||~", "!!")
            fixup = fixup.split("\n")
            fixout = ["", "{| class=\"wikitable\""]
            for i in xrange(len(fixup)):
                if fixup[i][0 : 2] == "||" or fixup[i][0 : 2] == "!!":
                    out = fixup[i].strip()[1 : ]
                    fixout.append(out[ : -2 if out[-2 : ] in ["||", "!!"] else 0])
                else:
                    print("Failed to parse item %d/%d: '%s'" % (i, len(fixup), fixup[i]))
                    sys.exit(-1)
                fixout.append("|}" if i == len(fixup) - 1 else "|-")

            # Construct output table text
            fullout = "\n".join(fixout)
            text = text[ : startpos] + fullout + text[endpos : ]
            startpos = startpos + len(fullout)

        # Repair multi-newlines
        text = re.sub(r"\n\n+", "\n\n", text, re.M)

        # Repair starting newlines
        text = text.strip()

        # Optional postprocessing stage
        text = postprocess.postprocess(text)	

        return text

    def split_text(self, text):
        output_parts = []
        split_regex = re.compile(self.regex_split_condition)
        for line in text.split("\n"):
            line += "\n"
            if len(output_parts) > 0 and (re.match(split_regex,line) == None): output_parts[-1] += line
            else: output_parts.append(line)
        return output_parts
