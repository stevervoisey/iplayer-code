#!/usr/bin/perl -sw


my $version = "1.00";

# Created by Steve Voisey (srv) 15 Feb 2018.
# email: [stevevoisey@yahoo.com]
#   #!C:\myApplications\Perl\Strawberry\perl\bin\perl -sw
#
# C:\Users\steve\.get_iplayer\download_history
#
# --outputtv 
#    get_iplayer --prefs-add --subdir --outputradio="/iplayer/radio/current"  --radiomode="hafstd,hafmed,vgood"
#    get_iplayer --prefs-add --subdir --outputtv="/iplayer/television/current"
#    get_iplayer --prefs-add --output="/iplayer/radio/current"
#    get_iplayer --prefs-add --no-purge
#
#    [root@nas01 iplayer]# get_iplayer --prefs-show
# Options in '/root/.get_iplayer/options'
#         radiomode = hafstd,hafmed,vgood
#         ffmpeg = /usr/local/bin/ffmpeg
#         outputtv = /iplayer/television/current
#        nopurge = 1
#        output = /iplayer/radio/current
#        outputradio = /iplayer/radio/current
#        subdir = 1
#
#    -radio=radio.list -television=tv.list -music=music.list
#
###my $radio = "radio.list";

use warnings;
use strict;
use Cwd;

# Enable $radio, etc to be defined from command line with -s and NOT raise errors with 'strict'
our ($radio, $tv, $music, $force);

my $environment;
my $code_home;
my $data_home;
my $profile_home;
my $playCommand;
my $share;
my $scripts;
my $conf;
my $logFile;
my $scriptFile;
my $options;

my @tv      = ();
my @radio   = ();
my @music   = ();

my $standardOptions;
my $voiceOptions;
my $musicOptions;
my $tvOptions;

my $divide = "=" x 80 . "\n";

#$dateTimeStamp = `date "+%Y%m%d_%H%M"`;
my $dateTimeStamp = "today";
chomp($dateTimeStamp);

my $thisDir = cwd();
chomp($thisDir);

unless(defined($environment)) { if ($^O =~ /MSWin32/) { $environment = "windows"; } else { $environment = "linux";} }

if ( $environment =~ /windows/i ) {
    unless(defined($code_home))  { $code_home = "D:/ME/Development/git/pycharm/iplayer-code"; }
    unless(defined($data_home))  { $data_home = "Z:/iplayer"; }
    unless(defined($profile_home))  { $profile_home = "Z:/iplayer/profile-dir"; }
    $playCommand = "get_iplayer.pl";
} else { 
    unless(defined($code_home))  { $code_home = "/myRaid/6TB/share/share02/Development/git/pycharm/iplayer-code"; }
    unless(defined($data_home))  { $data_home = "/myRaid/6TB/share/share02/iplayer"; }
    unless(defined($profile_home))  { $profile_home = "/myRaid/6TB/share/share02/iplayer/profile-dir"; }
    $playCommand = "get_iplayer";
}



#exit;

unless(defined($share))      { $share = $data_home; }
unless(defined($scripts))    { $scripts = "$code_home/scripts"; }
unless(defined($conf))       { $conf    = "$code_home/config"; }
unless(defined($logFile))    { $logFile = "$data_home/logs/autoGetIplayer_${dateTimeStamp}.log"; }
unless(defined($scriptFile)) { $scriptFile = "$data_home/batch_autoGetIplayer.bat"; }
unless(defined($options))    { $options = ""; }

$standardOptions = "--subdir --nopurge --profile-dir=${profile_home}";
$voiceOptions    = "--type=radio --outputradio=${share}/radio/current ${standardOptions}";
#$musicOptions    = "--type=radio --outputradio=${share}/music/current -radiomode=\"hafstd,hafmed,vgood\" ${standardOptions}";
$musicOptions    = "--type=radio --outputradio=${share}/music/current --radiomode=best ${standardOptions}";
$tvOptions       = "--type=tv --outputtv=${share}/television/current ${standardOptions} --ffmpeg-force";

if(defined($force))          { $options = "--force --overwrite"; }
if(defined($force))          { 1==1; }

print "${divide}version: ${version}\nenvironment: ${environment}\nlogfile: ${logFile}\n\n";

unless (open (OUT, ">$logFile"))   { die "cannot open output file $logFile $!"; }
unless (open (SCR, ">$scriptFile"))   { die "cannot open output file $scriptFile $!"; }

print SCR "setx IPLAY_DIR 'C:\\Program Files (x86)\\get_iplayer'\n";
print SCR "setx PERL_DIR 'C:\\Program Files (x86)\\get_iplayer\\perl'\n";

if(defined($radio)) { 
    print "radio file: $conf/$radio\n";
    if( -f "$conf/$radio" ) 
        { unless (open (RADIO, "<$conf/$radio"))   { die "cannot open input file $conf/$radio $!"; }}
    else 
        { print "not a file? $conf/$radio\n"; }
        
    @radio = <RADIO>;
    close RADIO;
}

if(defined($tv)) {
    print "television file: $conf/$tv\n";
    if( -f "$conf/$tv" ) { unless (open (TV, "<$conf/$tv"))   { die "cannot open input file $conf/$tv $!"; }}
    @tv = <TV>;
    close TV;
}

if(defined($music)) {
    print "music file: $conf/$music\n";
 
    if( -f "$conf/$music" ) { unless (open (MUSIC, "<$conf/$music"))   { die "cannot open input file $conf/$music $!"; }}
    @music = <MUSIC>;
    close MUSIC;
}

if ( @radio > 0 ) { process(\@radio, "radio"); }
if ( @tv > 0 )    { process(\@tv, "television"); }
if ( @music > 0 ) { process(\@music, "music"); }

print "\n\nautoGetIplayer finished.....\n";
exit;

###################################################################################
#  subroutine: process
###################################################################################

sub process {
    my $array_ref = $_[0];
    my $type      = $_[1];
    unless(defined($type)) { $type = "radio"; }
    my $command = "NONE";
    my $count = 0;
    my $out = "";
    my $line;
    foreach $line (@$array_ref) {
        my $series;
        $count++;
        $command = "NONE";
        my ($option, $program) = "";
        chomp($line);
        $line =~ s/\R\z//;

        if ($line =~ /^END-NOW$/) {last;}
        if ($line =~ /^\s*$/) {next;}
        if ($line =~ /^#/) {next;}
        if ($line =~ /^\|/) {next;}
        if ( $line =~ /\|/ || $line =~ /\// )    {
        #if ( $line =~ /\|/ )     {
            ( $program, $option ) = $line =~ /^(.*)[\|\/](.*)$/;
        } else {
            $program = $line;
        }
        if ( $option =~ /series/ ) { $series = "--pid-recursive"; } else { $series = ""; }
        
        print "line: $line\nprogram: [$program] option: [$option] series: [$series]\n";
        
        
        if ( $program =~ /^["'].*["']\s*$/ ) {
            if ( $type =~ /radio/i ) {
                $command = "$playCommand $voiceOptions ${program} ${options} --get ";
            }
            if ( $type =~ /television/i ) {
                $command = "$playCommand $tvOptions ${program} ${options} --get ";
            }
            if ( $type =~ /music/i ) {
                $command = "$playCommand $musicOptions ${program} ${options} --get";
            }
        }

        if ( $program =~ /^[\d\w]+$/ ) {
            if ( $type =~ /radio/i ) {
                $command = "$playCommand $voiceOptions --pid=${program} $series --get ${options}";
            }
            if ( $type =~ /television/i ) {
                $command = "$playCommand $tvOptions --pid=${program} $series --get ${options}";
            }
            if ( $type =~ /music/i ) {
                $command = "$playCommand $musicOptions --pid=${program} $series --get ${options}";
            }
        }           

        unless ( $command =~ /NONE/ ) {
            print "command: $command\n";
            $out = "";
            ####$out = `$command`;
            system($command);
            ###print "out: $out\n";
            print OUT "$command\n$out\n";
            ##perl.exe  "%IPLAY_DIR%"/get_iplayer.pl
            ##print OUT "$command\n";
            print SCR "perl.exe  \"%IPLAY_DIR%\"/$command\n";
        }
    }
}

close OUT;
close SCR;
