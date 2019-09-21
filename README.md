# DataView Helper Application

Why
--------------
Just a quick program to help me view some data files.

Features
--------
- Import CSV data files.
- Browse data in subsets, select the window you want to see.
- "chop" only the records/rows for the data you are viewing out of the
  original file and into a new file (CSV).  This lets you separate important
  records from all the others, by visually identifying interesting features in
  specific series/columns.
- Browse the data as single series/column vs index, or plot two series against
  each other.
- Calculate summary statistics (STDOUT)
- (New) Produce plot of Cumulative Distribution Function (CDF) (of vertical
  axis data series) along with other statistics.
- (New) Chop and Stats buttons now make copies of the view plot,
  automatically.

Requirements
-----------
- tkiner
- pandas
- numpy
- matplotlib
- logging
- warnings
- Number

### Copyright 2019 Paul R. DeStefano
>   This program is free software: you can redistribute it and/or modify
>   it under the terms of the GNU General Public License as published by
>   the Free Software Foundation, either version 3 of the License, or
>   (at your option) any later version.

>   This program is distributed in the hope that it will be useful,
>   but WITHOUT ANY WARRANTY; without even the implied warranty of
>   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
>   GNU General Public License for more details.

>   You should have received a copy of the GNU General Public License
>   along with this program.  If not, see <http://www.gnu.org/licenses/>.
