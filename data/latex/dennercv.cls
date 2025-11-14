
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{dennercv}[2025/11/11 v1.0 Academic CV class]

\LoadClass[12pt]{article}

% ----- Options ---------------------------------------------------------------
\RequirePackage{kvoptions}
\SetupKeyvalOptions{family=dennercv,prefix=dennercv@}
\DeclareStringOption[0072B2]{accentcolor} % hex color, default blue
\DeclareBoolOption[false]{sans}           % use sans-serif as main font
\DeclareBoolOption[true]{tight}           % tighter vertical spacing
\ProcessKeyvalOptions*

% ----- Packages --------------------------------------------------------------
\RequirePackage{iftex}
\ifPDFTeX
  \RequirePackage[T1]{fontenc}
  \RequirePackage[utf8]{inputenc}
  \RequirePackage{lmodern}
\else
  \RequirePackage{fontspec}
  \defaultfontfeatures{Ligatures=TeX}
  % Set a sensible default font depending on option
  \ifdennercv@sans
    \setmainfont{Arial}
    \setsansfont{Arial}
  \else
    \setmainfont{Times New Roman}
    \setsansfont{Arial}
  \fi
\fi

\RequirePackage{geometry}
\geometry{margin=1in, headheight=15pt}
\RequirePackage{xcolor}
\definecolor{accent}{HTML}{\dennercv@accentcolor}
\RequirePackage{microtype}
\RequirePackage[colorlinks=true,linkcolor=black,urlcolor=accent,citecolor=accent]{hyperref}
\RequirePackage{enumitem}
\RequirePackage{array}
\RequirePackage{ragged2e}
\RequirePackage{etoolbox}
\RequirePackage{fancyhdr}

% ----- Page style ------------------------------------------------------------
\pagestyle{fancy}
\fancyhf{}
\rhead{\thepage}
\renewcommand{\headrulewidth}{0pt}

% ----- Global spacing --------------------------------------------------------
\ifdennercv@tight
  \setlength{\parskip}{4pt}
\else
  \setlength{\parskip}{8pt}
\fi
\setlength{\parindent}{0pt}
\setlist{nosep}

% ----- Identity fields -------------------------------------------------------
\newcommand{\cvname}{}
\newcommand{\cvpronouns}{}
\newcommand{\cvheadline}{}
\newcommand{\cvcontact}{}
\newcommand{\cvaddress}{}

\newcommand{\name}[1]{\renewcommand{\cvname}{#1}}
\newcommand{\pronouns}[1]{\renewcommand{\cvpronouns}{#1}}
\newcommand{\headline}[1]{\renewcommand{\cvheadline}{#1}}
\newcommand{\contact}[1]{\renewcommand{\cvcontact}{#1}}
\newcommand{\address}[1]{\renewcommand{\cvaddress}{#1}}

% ----- Title block -----------------------------------------------------------
\newcommand{\makecvtitle}{%
  \begin{center}
    {\Huge\bfseries \cvname}%
    \ifstrempty{\cvpronouns}{}{ \quad \textit{(\cvpronouns)}}\par
    \vspace{0.3em}
    \ifstrempty{\cvheadline}{}{{\large\color{accent}\textbf{\cvheadline}}\par}
    \vspace{0.6em}
    \ifstrempty{\cvcontact}{}{{\small \cvcontact\par}}
    \ifstrempty{\cvaddress}{}{{\small \cvaddress\par}}
  \end{center}
  \vspace{0.6em}
  {\color{accent}\rule{\linewidth}{0.6pt}}
  \vspace{0.6em}
}

% ----- Sectioning ------------------------------------------------------------
\newcommand{\cvsection}[1]{%
  \vspace{0.3\baselineskip}
  {\large\bfseries #1}\par
  {\color{accent}\rule{\linewidth}{0.4pt}}
  \vspace{0.2\baselineskip}
}

% ----- Entries (dates on the left) ------------------------------------------
\newlength{\datelabelwidth}
\setlength{\datelabelwidth}{3.6cm}

\newenvironment{cventries}{%
  \begin{description}[style=nextline,leftmargin=\datelabelwidth,labelwidth=\datelabelwidth,labelsep=0.8cm,font=\normalfont\scshape\color{accent}]%
}{%
  \end{description}%
}

\newenvironment{cvitems}{\begin{itemize}[leftmargin=*,topsep=2pt,itemsep=2pt]}{\end{itemize}}

\newcommand{\cventry}[5]{%
  \item[#1] \textbf{#2} — #3%
  \ifstrempty{#4}{}{, #4}%
  \ifstrempty{#5}{}{%
    \par\begin{cvitems}#5\end{cvitems}}%
}

% ----- Tags / keywords -------------------------------------------------------
\newcommand{\cvtag}[1]{%
  \begingroup
  \setlength{\fboxsep}{0.6ex}\setlength{\fboxrule}{0.4pt}%
  \color{accent}\fbox{\color{black}\footnotesize #1}%
  \endgroup
  \hspace{0.3em}
}

% ----- Publications helper (works if biblatex is loaded in the document) ----
\makeatletter
\newcommand{\printpublications}[1][]{%
  \@ifundefined{printbibliography}{%
    \cvsection{Publications}%
    % (Load biblatex in your .tex to enable automatic printing)
  }{%
    \printbibliography[title={Publications},#1]%
  }%
}
\makeatother
