
SUP GUYS - sorry in advance for the long ass intro
I'll try to keep this brief, but it's all pretty important info


The big goal right now is trying to get the moca data to shift to
automatically align with biostamp data.

To align horizontally, we find the peaks of the data and align the
first peak of both datasets.
To align vertically, I'm thinking take the avg height of the peaks?


**NOTE**
We are graphing both horizontal over time and vertical over time,
NOT vertical over horizontal or vice versa.
Also, these graph axes are seconds and meters, just not labelled yet.
********


Another big issue is the distance and heights for the peaks.
The module that I am using is called spicy.signal.find_peaks
I'm not 100% sure how it works, but I know that it does if we give
it the right numbers.

I've learned that distance and height are the two main factors to whether
this will work.

Distance -- the min distance between each peak point.
    I've figured out that for Chest AA, a distance of 300 works for slow
    movements and 100 works for fast

Height -- still a mystery to me. I think it's the general height that it
searches for the peaks?
    I know that when the data starts at 0m and goes up to x meters, the
    height is x.
    But unadjusted, I had some data that went from -1.2 to -0.7 and the
    height was -0.7.
I have a feeling that once the moca and bio data is adjusted to match, the height
will be the max displacement of the movement per axis


I also recently changed everything into classes: mocaData and bioData
mocaData has private fields for x, y, and z but that's not accurate data.
Z should be accurate but things got wack with x and y.
Instead, I have self.vert and self.horiz which are the vertical and horizontal
axes.

I'll try to give more info about the classes in the file itself.
I also tried to make it so that some fields were private and others
were public so that they were easy to use, but I think that was
probably a mistake cause I keep confusing myself :(

I also know that my styling is shit don't judge me lol

Good luckkkkkk
