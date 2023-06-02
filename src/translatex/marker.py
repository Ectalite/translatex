from TexSoup import TexSoup
from TexSoup.data import *
from TexSoup.data import TexUnNamedEnv, TexExpr
from typing import Dict, List, Type

MATH_ENVS: List[Type[TexUnNamedEnv]] = [TexMathEnv, TexMathModeEnv, TexDisplayMathEnv, TexDisplayMathModeEnv]
TEXT_COMMANDS: List[str] = ["text", "textsf", "textrm", "textnormal"]


class Marker:

    def __init__(self, latex: str) -> None:
        self.soup: TexNode = TexSoup(latex)
        self.marker_count: int = 0
        self.marker_format: str = "//{}//"
        self.marker_store: Dict[int, str | list] = dict()

    def __str__(self) -> str:
        return str(self.soup)

    def __next_marker__(self) -> str:
        self.marker_count += 1
        return self.marker_format.format(self.marker_count)

    def set_marker_format(self, format_str: str) -> None:
        # TODO: implement format string check (if it has only a single occurrence of "{}")
        self.marker_format = format_str

    def __mark_node_name__(self, node: TexNode) -> None:
        previous_name: str = node.name
        if type(node.expr) is TexNamedEnv:
            node.name = self.__next_marker__()
            self.marker_store.update({self.marker_count: previous_name})
        elif type(node.expr) is TexCmd:
            if node.name in ["label", "ref"]:
                return
            node.name = self.__next_marker__()
            self.marker_store.update({self.marker_count: previous_name})

    def __mark_node_contents__(self, node: TexNode, replace_range: range = None) -> None:
        # TODO: Test if lists need deep copying
        if replace_range is None:
            previous_contents: list = node.contents
            node.contents = [self.__next_marker__()]
            self.marker_store.update({self.marker_count: previous_contents})
        else:
            previous_contents: list = node.contents[replace_range.start:replace_range.stop]

            templs = list(node.contents)
            del templs[replace_range.start:replace_range.stop]

            # del node.contents[replace_range.start:replace_range.stop]

            # node.contents = node.contents[:replace_range.start] + node.contents[replace_range.stop:]

            # index = replace_range.start
            # for __ in replace_range:
            #     node.contents.pop(index)

            # node.contents.insert(replace_range.start, self.__next_marker__())

            templs.insert(replace_range.start, self.__next_marker__())
            # templs[1] = TexExpr(templs[1].name, (templs[1].args, ))
            templs[1] = str(templs[1]) # to be continued... (expression stays a string and doesn't get recursed into later)
            node.contents = templs
            self.marker_store.update({self.marker_count: previous_contents})

    def __traverse_ast_aux__(self, node: TexNode):
        if len(node.children) == 0:
            self.__mark_node_name__(node)
        elif type(node.expr) in MATH_ENVS:
            continue_recursion = False
            for descendant in node.descendants:
                if type(descendant) is TexNode and descendant.name in TEXT_COMMANDS:
                    continue_recursion = True
                    break
            if continue_recursion:

                ranges_to_mark: List[range] = list()
                start: int = -1
                for i, content in enumerate(node.contents):
                    if start == -1 and (type(content) is not TexNode or content.name not in TEXT_COMMANDS):
                        start = i
                    elif start != -1 and type(content) is TexNode and content.name in TEXT_COMMANDS:
                        ranges_to_mark.append(range(start, i))
                        start = -1
                    # else:
                    #     start = i
                for range_to_mark in ranges_to_mark:
                    self.__mark_node_contents__(node, range_to_mark)

                for current_node in node.children:
                    self.__traverse_ast_aux__(current_node)

            else:
                self.__mark_node_contents__(node)
        else:
            for current_node in node.children:
                self.__traverse_ast_aux__(current_node)
            self.__mark_node_name__(node)

    def traverse_ast(self):
        self.__traverse_ast_aux__(self.soup.find("document"))


m = Marker(r"""
\documentclass{article}
\usepackage[T1]{fontenc}
\usepackage[french]{babel}
\usepackage{amsthm,amssymb,amsmath,xcolor}
\usepackage{hyperref}
\hypersetup{
	colorlinks,
	linkcolor={red},
	urlcolor={purple}
}

\newtheorem{definition}{Définition}
\newtheorem{theorem}[definition]{Théorème}
\newtheorem{remark}[definition]{Remarque}

\begin{document}
	\author{Efe ERKEN}
	\date{octobre 2021}
	\title{Le \LaTeX\ c'est bon, mangez-en}
	\maketitle
	
	\section{Introduction}
	Depuis la nuit des temps, ou presque, l’humanité a cherché à rendre compte de \underline{vérités universelles}. Parmi les folles formes foisonnantes, nous en retiendrons trois.
	\label{sec:label1}
	
	\begin{definition}
	\textbf{Loi zozotérique.} Quelle que soit l’absurdité d’une proposition, il existera toujours au moins 72\% de la population pour y croire.
	\label{def:label1}
	\end{definition}

	\begin{definition}
	\textbf{Loi tactique.} La pataphysique rit.
	\label{def:label2}
	\end{definition}

	\begin{definition}
	\textbf{Loi des piques.} Un fois ça va, dix fois bonjour les dégâts.
	\label{def:label3}
	\end{definition}	

	\noindent Dans cet article nous proposons :
	\begin{enumerate}
		\item une approche \textbf{homogène} permettant d’affiner l’estimation de la proportion zozotérique $\Lambda\,(\mathcal{P})$ en fonction de la proposition $\mathcal{P}$ ;
		\item une implémentation \textsc{Python} d’un algorithme de calcul effectif de $\Lambda\,(\mathcal{P})$.
		\item Le grand oral, en 69 mots.
	\end{enumerate}
	
	\begin{theorem}
		Étant donnée une proposition $\mathcal{P}$, la proportion zozotérique $\Lambda\,(\mathcal{P})$ égale sa crédulance relative à la population.
		\label{theo:label1}
	\end{theorem}
	
	\begin{theorem}
		Soit Pop un échantillon de population bleue et $\mathcal{P}$ une proposition homogène exprimée universellement par quantification imbriquée. Alors
		\[
		\Lambda\,(\mathcal{P}) \geqslant \, \; \sum_{72}^{10} \frac{\int_{-151}^{69} - \frac{3\mu}{2} + 4x - \pi + 2 \, \: \; \mathrm{d}x}{\sum_{10}^{72} - 5\alpha + \frac{x}{7} + 7 - \frac{18}{7\sigma} - \frac{5}{\alpha}} \, \: \;  \mathrm{,}
		\text{hello there}
		\]
		avec égalité presque sûrement si, et seulement si, $\mathcal{P}$ est la proposition \og brouillard en matinée, belle et claire journée \fg.
		\label{theo:label2}
	\end{theorem}
	
	\begin{remark}
		La Section \ref{sec:label2} contient la démonstration du Théorème \ref{theo:label2}.
	\end{remark}
	
	\begin{remark}
		En observant que ce théorème est en fait effectif, nous en déduisons également un algorithme de complexité $O(n(\mathcal{P}))$, où $n(\mathcal{P})$ est le nombre de caractères nécessaire à exprimer $\mathcal{P}$ en \href{https://lolcode.org/}{\textsc{Lolcode}}.
	\end{remark}
	
	\section{Preuve du Théorème \ref{theo:label2}}
	Les détails sont laissés au lecteur. À la place, révisons un peu nos classiques.
	\label{sec:label2}
	
	\subsection{Liste des personnages}
	\label{subsec:label1}
	
	\begin{description}
		\item[Don Fernand :] premier roi de Castille
		\item[Donna Urraque :] infante de Castille
		\item[Don Diègue :] \emph{père de don Rodrigue}
		\item[Don Gomès :] \emph{comte de Gormas et père de Chimène}
		\item[Don Rodrigue :] \textsc{amant de Chimène}
		\item[Don Sanche :] \textsc{amoureux de Chimène}
		\item[Don Arias :] \textbf{gentilhomme castillan}
		\item[Don Alonse :] \emph{gentilhomme castillan}
		\item[Chimène :] \emph{fille de don Gomès}
		\item[Léonor :] \textbf{gouvernante de l’infante}
		\item[Elvire :] gouvernante de Chimène
		\item[Le page :] \textbf{un page de l’infante}
	\end{description}
	
	\subsection{Acte 10, scène 151}
	\label{subsec:label2}
	
	\begin{itemize}
		\item[$\blacksquare$] \textbf{Don Rodrigue} (\emph{absolument désenchantée}) \\
		\textsf{Mon honneur lui fera mille autres ennemis.}
		\item[$\blacksquare$] \textbf{Don Sanche} (\emph{dans un état de sidération intersidérale}) \\
		\textsf{Ma vengeance est perdue et mes desseins trahis :}
		\item[$\blacksquare$] \textbf{Chimène} (\emph{le ton enjoué}) \\
		\textsf{Le guerrier sans courage et le perfide amant.}
		\item[$\blacksquare$] \textbf{Chimène} (\emph{le visage défait}) \\
		\textsf{Rodrigue a du courage.}
		\item[$\blacksquare$] \textbf{Don Alonse} (\emph{absolument désenchantée}) \\
		\textsf{Mais pour ne troubler pas une si belle flamme ;}
		\item[$\blacksquare$] \textbf{Léonor} (\emph{d’une voix rauque}) \\
		\textsf{On les laisse passer ; tout leur paraît tranquille ;}
		\item[$\blacksquare$] \textbf{Don Rodrigue} (\emph{ regard incisif}) \\
		\textsf{Ma main seule du mien a su venger l’offense,}
		\item[$\blacksquare$] \textbf{Chimène} (\emph{le ton enjoué}) \\
		\textsf{Dans la nuit qui survient troublerait trop la ville :}
	\end{itemize}
	
\end{document}
""")

m.traverse_ast()
print(str(m))
